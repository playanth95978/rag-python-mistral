"""Composition des dépendances et gestion de leur durée de vie."""

from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator

from app.core.config import Settings
from app.infrastructure.mistral.chunking_adapter import MistralChunkingAdapter
from app.infrastructure.mistral.client import MistralClient
from app.infrastructure.mistral.embedding_adapter import MistralEmbeddingAdapter
from app.infrastructure.mistral.llm_adapter import MistralLLMAdapter
from app.infrastructure.vector_store.vespa_adapter import VespaAdapter
from app.services.container import Services
from app.services.generation.chat_service import ChatService
from app.services.generation.rag_service import RAGService
from app.services.ingestion.indexing_service import IndexingService
from app.services.ingestion.ingestion_service import IngestionService
from app.services.retrieval.retrieval_service import RetrievalService


@asynccontextmanager
async def build_services(settings: Settings) -> AsyncIterator[Services]:
    async with AsyncExitStack() as resources:
        client = MistralClient(settings)
        resources.push_async_callback(client.aclose)
        embeddings = MistralEmbeddingAdapter(client)
        store = VespaAdapter(embeddings, settings.vespa_url)
        resources.push_async_callback(store.aclose)
        retrieval = RetrievalService(store)
        yield Services(
            ingestion=IngestionService(MistralChunkingAdapter(), IndexingService(embeddings, store)),
            retrieval=retrieval,
            rag=RAGService(retrieval, MistralLLMAdapter(client)),
            chat=ChatService(
                MistralLLMAdapter(client, settings.mistral_direct_chat_model, max_tokens=4096),
                settings.mistral_direct_chat_model,
            ),
        )
