from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_services
from app.api.v1.schemas.job import JobIngestionRequest, JobIngestionResponse, JobOfferResponse
from app.services.container import Services

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=list[JobOfferResponse])
async def search_jobs(
    services: Annotated[Services, Depends(get_services)],
    keywords: str | None = None,
    location: str | None = None,
    country: Annotated[str | None, Query(description="Marche Adzuna : fr, gb, au…")] = None,
    source: Annotated[list[str] | None, Query(description="ADZUNA, EMPLOI_NC ; vide = toutes")] = None,
):
    offers = await services.jobs.search(keywords, location, country, source)
    return [asdict(offer) for offer in offers]


@router.post("/jobs/ingest", response_model=JobIngestionResponse)
async def ingest_jobs(request: JobIngestionRequest, services: Annotated[Services, Depends(get_services)]):
    result = await services.job_ingestion.ingest(
        request.keywords, request.location, request.country, request.sources
    )
    return asdict(result)
