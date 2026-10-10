from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_services
from app.api.v1.schemas.document import DocumentRequest, DocumentResponse
from app.services.container import Services

router = APIRouter(tags=["documents"])


@router.post("/documents", status_code=201, response_model=DocumentResponse)
async def ingest(document: DocumentRequest, services: Annotated[Services, Depends(get_services)]):
    return asdict(await services.ingestion.ingest(document.title, document.text))
