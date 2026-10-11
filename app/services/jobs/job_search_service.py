import asyncio

from app.domain.interfaces.job_provider import JobProvider
from app.domain.models.job_offer import JobOffer


class JobSearchService:
    """Interroge les fournisseurs en parallele et concatene leurs offres."""

    def __init__(self, providers: list[JobProvider]):
        self.providers = providers

    @property
    def sources(self) -> list[str]:
        return [provider.source for provider in self.providers]

    async def search(
        self,
        keywords: str | None = None,
        location: str | None = None,
        country: str | None = None,
        sources: list[str] | None = None,
    ) -> list[JobOffer]:
        wanted = {source.upper() for source in sources} if sources else None
        selected = [p for p in self.providers if wanted is None or p.source in wanted]
        results = await asyncio.gather(*(p.fetch_jobs(keywords, location, country) for p in selected))
        return [offer for offers in results for offer in offers]
