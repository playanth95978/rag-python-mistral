from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_services
from app.api.v1.schemas.chat import AnswerResponse, QuestionRequest, SearchResponse
from app.services.container import Services

router = APIRouter(tags=["chat"])


@router.post("/search", response_model=SearchResponse)
async def search(request: QuestionRequest, services: Annotated[Services, Depends(get_services)]):
    return {
        "sources": [asdict(hit) for hit in await services.retrieval.search(request.question, request.top_k)]
    }


@router.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest, services: Annotated[Services, Depends(get_services)]):
    return asdict(await services.rag.ask(request.question, request.top_k))
