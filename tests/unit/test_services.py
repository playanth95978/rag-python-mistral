import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import InvalidEmbedding, NoDocuments
from app.domain.interfaces.embeddings import EmbeddingBatch
from app.domain.models.chunk import SearchHit
from app.infrastructure.mistral.chunking_adapter import MistralChunkingAdapter
from app.services.generation.rag_service import RAGService
from app.services.ingestion.indexing_service import IndexingService
from app.services.ingestion.ingestion_service import IngestionService
from app.services.retrieval.retrieval_service import RetrievalService
from scripts.kv_cache_demo import run_demo
from tests.fakes import FakeEmbeddings, FakeLLM


def test_ingestion_preserves_text_offsets_and_embedding_usage():
    store = SimpleNamespace(index_document=AsyncMock())
    service = IngestionService(MistralChunkingAdapter(), IndexingService(FakeEmbeddings(), store))
    text = "Python " + "x" * 2200
    result = asyncio.run(service.ingest("Offre", text))
    document, chunks, total_tokens = store.index_document.call_args.args
    assert result.document_id == document.id
    assert result.chunks == 3
    assert "".join(c.text for c in chunks) == text
    assert [c.start_offset for c in chunks] == [0, 1000, 2000]
    assert all(len(c.embedding) == 1024 and c.title == "Offre" for c in chunks)
    assert total_tokens == 15


def test_incomplete_embeddings_never_write_index():
    store = SimpleNamespace(index_document=AsyncMock())
    embeddings = SimpleNamespace(embed=AsyncMock(return_value=EmbeddingBatch([], 0)))
    service = IngestionService(MistralChunkingAdapter(), IndexingService(embeddings, store))
    with pytest.raises(InvalidEmbedding):
        asyncio.run(service.ingest("A", "Python"))
    store.index_document.assert_not_called()


def test_generation_uses_same_order_for_context_and_citations():
    hits = [
        SearchHit("1", "Offre A", "Python", 1, "source", "char:0-6"),
        SearchHit("2", "Offre B", "Java", 0.5, "source2", "char:0-4"),
    ]
    store = SimpleNamespace(search=AsyncMock(return_value=hits))
    llm = FakeLLM()
    answer = asyncio.run(RAGService(RetrievalService(store), llm).ask("Compétences ?", 2))
    assert "[1] Offre A\nPython" in llm.messages[1].content
    assert "[2] Offre B\nJava" in llm.messages[1].content
    assert llm.messages[-1].content == "Compétences ?"
    assert [(s.id, s.citation) for s in answer.sources] == [("1", 1), ("2", 2)]
    assert answer.cached_prompt_tokens == 64


def test_empty_retrieval_does_not_call_llm():
    store = SimpleNamespace(search=AsyncMock(return_value=[]))
    llm = SimpleNamespace(complete=AsyncMock())
    with pytest.raises(NoDocuments):
        asyncio.run(RAGService(RetrievalService(store), llm).ask("Question ?", 3))
    llm.complete.assert_not_called()


def test_kv_cache():
    assert run_demo() == (10, 4)


def test_job_ingestion_indexes_offers_with_stable_ids_and_counts_failures():
    from datetime import datetime

    from app.core.exceptions import MistralUnavailable
    from app.domain.models.document import IngestionResult
    from app.domain.models.job_offer import JobOffer
    from app.services.jobs.job_ingestion_service import JobIngestionService

    offers = [
        JobOffer(
            source="EMPLOI_NC",
            source_id="u1",
            title="Comptable",
            description="Tenue des comptes",
            company="ACME",
            location="Nouméa",
            published_at=datetime(2026, 10, 1),
        ),
        JobOffer(source="ADZUNA", source_id="a2", title="Dev", description="Java"),
    ]

    class FakeSearch:
        async def search(self, *args):
            return offers

    class FakeIngestion:
        def __init__(self):
            self.documents = []

        async def ingest_document(self, document):
            self.documents.append(document)
            if document.source_id.startswith("ADZUNA"):
                raise MistralUnavailable()
            return IngestionResult(document_id=document.id, chunks=1)

    ingestion = FakeIngestion()
    result = asyncio.run(JobIngestionService(FakeSearch(), ingestion).ingest("comptable"))

    assert (result.fetched, result.indexed, result.chunks, result.failed) == (2, 1, 1, 1)
    first = ingestion.documents[0]
    assert first.source_id == "EMPLOI_NC:u1"
    assert "Lieu : Nouméa" in first.text and "Publiee le : 2026-10-01" in first.text
    assert first.text.endswith("Tenue des comptes")
