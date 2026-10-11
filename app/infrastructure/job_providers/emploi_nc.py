from typing import Any

from app.domain.models.job_offer import JobOffer
from app.infrastructure.job_providers.base import AbstractJobProvider

RECORDS_API = (
    "https://data.gouv.nc/api/explore/v2.1/catalog/datasets/"
    "offres-d-emploi-deposees-sur-le-site-emploi-nc/records"
)
OFFER_URL_PREFIX = "https://emploi.nc/offers/"
PAGE_SIZE = 50


class EmploiNcProvider(AbstractJobProvider):
    """Offres emploi.nc via l'API Open Data NC (Opendatasoft v2.1), sans authentification."""

    source = "EMPLOI_NC"

    def supports(self, url: str) -> bool:
        return any(domain in (url or "") for domain in ("emploi.nc", "emploi.gouv.nc"))

    async def fetch_jobs(
        self, keywords: str | None = None, location: str | None = None, country: str | None = None
    ) -> list[JobOffer]:
        params = {
            "where": _build_where(keywords, location),
            "limit": PAGE_SIZE,
            "offset": 0,
            "order_by": "date_debut desc",
        }
        data = await self._get_json(RECORDS_API, params)
        return [self._map(record) for record in (data or {}).get("results") or [] if record]

    def _map(self, r: dict[str, Any]) -> JobOffer:
        uuid = r.get("uuid")
        return JobOffer(
            source=self.source,
            source_id=uuid,
            title=(r.get("titre") or "").strip(),
            description=_build_description(r),
            company=r.get("enseigne") or r.get("designation"),
            location=r.get("ville") or r.get("ville_physique"),
            country="NC",
            apply_url=f"{OFFER_URL_PREFIX}{uuid}#top" if uuid else OFFER_URL_PREFIX,
            contract_type=r.get("type_contrat"),
            published_at=self._parse_date(r.get("date_debut")),
            remote=False,
        )


def _sanitize(value: str) -> str:
    return value.replace('"', " ").strip()


def _build_where(keywords: str | None, location: str | None) -> str:
    where = 'statut="ACTIVE"'
    if keywords:
        where += f' and search("{_sanitize(keywords)}")'
    if location:
        where += f' and search(ville, "{_sanitize(location)}")'
    return where


def _build_description(r: dict[str, Any]) -> str:
    """Le champ description est souvent vide : on synthetise un texte de repli."""
    if r.get("description"):
        return r["description"]
    text = f"Offre {r.get('titre') or 'emploi'}"
    if r.get("type_contrat"):
        text += f" — {r['type_contrat']}"
    city = r.get("ville") or r.get("ville_physique")
    if city:
        text += f" à {city}"
    text += "."
    if r.get("email"):
        text += f" Contact : {r['email']}."
    if r.get("telephone"):
        text += f" Tél : {r['telephone']}."
    return text + " Source : emploi.nc."
