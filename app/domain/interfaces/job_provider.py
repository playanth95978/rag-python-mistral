from typing import Protocol

from app.domain.models.job_offer import JobOffer


class JobProvider(Protocol):
    """Strategie de recuperation d'offres : une implementation par source."""

    source: str

    def supports(self, url: str) -> bool: ...

    async def fetch_jobs(
        self, keywords: str | None = None, location: str | None = None, country: str | None = None
    ) -> list[JobOffer]: ...
