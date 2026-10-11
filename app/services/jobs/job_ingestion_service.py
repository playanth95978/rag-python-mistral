import logging
from dataclasses import dataclass

from app.core.exceptions import ApplicationError
from app.domain.models.document import Document
from app.domain.models.job_offer import JobOffer
from app.services.ingestion.ingestion_service import IngestionService
from app.services.jobs.job_search_service import JobSearchService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JobIngestionResult:
    fetched: int
    indexed: int
    chunks: int
    failed: int


class JobIngestionService:
    """Recupere les offres puis les decoupe, les vectorise et les indexe dans Vespa."""

    def __init__(self, search: JobSearchService, ingestion: IngestionService):
        self.search = search
        self.ingestion = ingestion

    async def ingest(
        self,
        keywords: str | None = None,
        location: str | None = None,
        country: str | None = None,
        sources: list[str] | None = None,
    ) -> JobIngestionResult:
        offers = await self.search.search(keywords, location, country, sources)
        indexed = chunks = failed = 0
        # Sequentiel : un appel d'embedding par offre, pour menager le quota Mistral.
        for offer in offers:
            try:
                result = await self.ingestion.ingest_document(to_document(offer))
            except ApplicationError as error:
                logger.warning("Offre %s:%s non indexee : %s", offer.source, offer.source_id, error)
                failed += 1
                continue
            indexed += 1
            chunks += result.chunks
        return JobIngestionResult(fetched=len(offers), indexed=indexed, chunks=chunks, failed=failed)


def to_document(offer: JobOffer) -> Document:
    """L'id derive de source + source_id : reingerer une offre la met a jour au lieu de la dupliquer."""
    header = [
        ("Source", offer.source),
        ("Entreprise", offer.company),
        ("Lieu", offer.location),
        ("Pays", offer.country),
        ("Contrat", offer.contract_type),
        ("Teletravail", "oui" if offer.remote else None),
        ("Publiee le", offer.published_at.date().isoformat() if offer.published_at else None),
        ("Postuler", offer.apply_url),
    ]
    lines = [f"{label} : {value}" for label, value in header if value]
    key = offer.source_id or offer.apply_url or offer.title
    return Document(
        source_id=f"{offer.source}:{key}",
        title=offer.title,
        text="\n".join([offer.title, *lines, "", offer.description]),
    )
