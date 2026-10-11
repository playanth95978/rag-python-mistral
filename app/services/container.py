from dataclasses import dataclass

from app.services.generation.chat_service import ChatService
from app.services.generation.rag_service import RAGService
from app.services.ingestion.ingestion_service import IngestionService
from app.services.jobs.job_search_service import JobSearchService
from app.services.retrieval.retrieval_service import RetrievalService


@dataclass(frozen=True)
class Services:
    ingestion: IngestionService
    retrieval: RetrievalService
    rag: RAGService
    chat: ChatService | None = None
    jobs: JobSearchService | None = None
