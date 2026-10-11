import html
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import httpx

from app.domain.models.job_offer import JobOffer

logger = logging.getLogger(__name__)

_REMOTE_MARKERS = ("remote", "télétravail", "teletravail", "work from home", "anywhere")
_TAGS = re.compile(r"<[^>]+>")


class AbstractJobProvider(ABC):
    """Socle commun : client HTTP partage, decodage JSON et normalisations.

    Les erreurs reseau sont journalisees puis absorbees : une source indisponible
    doit donner "aucun resultat", pas faire echouer toute la recherche.
    """

    source: str

    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    @abstractmethod
    def supports(self, url: str) -> bool: ...

    @abstractmethod
    async def fetch_jobs(
        self, keywords: str | None = None, location: str | None = None, country: str | None = None
    ) -> list[JobOffer]: ...

    async def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any] | None:
        try:
            response = await self.http.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as error:
            logger.error("%s fetch failed for %s: %s", self.source, url, error)
            return None

    @staticmethod
    def _strip_html(value: str | None) -> str:
        return " ".join(html.unescape(_TAGS.sub(" ", value or "")).split())

    @staticmethod
    def _detect_remote(*fields: str | None) -> bool:
        haystack = " ".join(f for f in fields if f).lower()
        return any(marker in haystack for marker in _REMOTE_MARKERS)

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
