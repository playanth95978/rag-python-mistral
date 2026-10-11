import logging
from typing import Any

import httpx

from app.core.config import Settings
from app.domain.models.job_offer import JobOffer
from app.infrastructure.job_providers.base import AbstractJobProvider

logger = logging.getLogger(__name__)

API_BASE = "https://api.adzuna.com/v1/api/jobs"


class AdzunaProvider(AbstractJobProvider):
    """API Adzuna (mots-cles + pays). Pas d'endpoint NC : voir EmploiNcProvider."""

    source = "ADZUNA"

    def __init__(self, http: httpx.AsyncClient, settings: Settings):
        super().__init__(http)
        self.settings = settings

    def supports(self, url: str) -> bool:
        return "adzuna.com" in (url or "")

    async def fetch_jobs(
        self, keywords: str | None = None, location: str | None = None, country: str | None = None
    ) -> list[JobOffer]:
        app_id = self.settings.adzuna_app_id
        app_key = self.settings.adzuna_app_key.get_secret_value()
        if not app_id or not app_key:
            logger.warning("Adzuna non configure (ADZUNA_APP_ID / ADZUNA_APP_KEY)")
            return []

        market = (country or self.settings.adzuna_country).lower()
        params: dict[str, Any] = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": self.settings.adzuna_results_per_page,
        }
        if keywords:
            params["what"] = keywords
        if location:
            params["where"] = location

        data = await self._get_json(f"{API_BASE}/{market}/search/1", params)
        return [self._map(job, market) for job in (data or {}).get("results") or [] if job]

    def _map(self, job: dict[str, Any], market: str) -> JobOffer:
        location = job.get("location") or {}
        area = location.get("area") or []
        title = job.get("title") or ""
        description = self._strip_html(job.get("description"))
        city = location.get("display_name")
        return JobOffer(
            source=self.source,
            source_id=job.get("id"),
            title=title,
            description=description,
            company=(job.get("company") or {}).get("display_name"),
            location=city,
            country=area[0] if area else market.upper(),
            apply_url=job.get("redirect_url"),
            contract_type=job.get("contract_type") or job.get("contract_time"),
            salary_min=_rounded(job.get("salary_min")),
            salary_max=_rounded(job.get("salary_max")),
            published_at=self._parse_date(job.get("created")),
            remote=self._detect_remote(title, city, description),
        )


def _rounded(value: float | None) -> int | None:
    return None if value is None else round(value)
