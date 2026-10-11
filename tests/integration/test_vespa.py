import asyncio
import os
from uuid import uuid4

import pytest

from app.core.config import Settings
from app.domain.models.chunk import Chunk
from app.domain.models.document import Document
from app.infrastructure.mistral.chunking_adapter import MistralChunkingAdapter
from app.infrastructure.vector_store.vespa_adapter import VespaAdapter
from app.services.generation.rag_service import RAGService
from app.services.ingestion.indexing_service import IndexingService
from app.services.ingestion.ingestion_service import IngestionService
from app.services.retrieval.retrieval_service import RetrievalService
from tests.fakes import FakeEmbeddings, FakeLLM


@pytest.mark.integration
@pytest.mark.skipif(os.getenv("VESPA_INTEGRATION") != "1", reason="Activer VESPA_INTEGRATION=1")
def test_cv_collection_is_separate_from_jobs():
    async def check():
        embeddings = FakeEmbeddings()
        endpoint = Settings().vespa_url
        cvs = VespaAdapter(embeddings, endpoint, collection_name="cv_user")
        jobs = VespaAdapter(embeddings, endpoint)
        marker = "cv-isolation-" + str(uuid4())
        document = Document(marker, "CV test", "Python " + marker)
        vector = (await embeddings.embed([document.text])).vectors[0]
        chunk = Chunk(marker, document.title, document.text, 0, len(document.text), vector)
        try:
            await cvs.index_document(document, [chunk], 5)
            for _ in range(50):
                hits = await cvs.search(document.text, 100)
                if any(hit.source_id == marker for hit in hits):
                    break
                await asyncio.sleep(0.2)
            assert any(hit.source_id == marker for hit in hits)
            assert all(hit.source_id != marker for hit in await jobs.search(document.text, 100))
        finally:
            await cvs.index.delete_document(document.id)
            await cvs.aclose()
            await jobs.aclose()

    asyncio.run(check())


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("VESPA_INTEGRATION") != "1", reason="Activer VESPA_INTEGRATION=1 pour Vespa réel"
)
def test_real_hybrid_search_persistence_and_generation():
    async def check():
        embeddings = FakeEmbeddings()
        endpoint = Settings().vespa_url
        store = VespaAdapter(embeddings, endpoint)
        ingestion = IngestionService(MistralChunkingAdapter(), IndexingService(embeddings, store))
        retrieval = RetrievalService(store)
        ids = []
        other = None
        try:
            for title, text in [
                ("A", "Python FastAPI"),
                ("B", "Java Spring"),
                ("C", "Python FastAPI orbitalunik"),
            ]:
                ids.append((await ingestion.ingest(title, text)).document_id)
            hits = []
            for _ in range(50):
                hits = await store.search("Python orbitalunik", 3)
                if len(hits) == 3:
                    break
                await asyncio.sleep(0.2)
            assert hits[0].title == "C"
            assert hits[0].score > next(h.score for h in hits if h.title == "A")
            assert hits[0].locator.startswith("char:")
            other = VespaAdapter(embeddings, endpoint)
            assert (await other.search("Python orbitalunik", 1))[0].title == "C"
            answer = await RAGService(retrieval, FakeLLM()).ask("Python orbitalunik", 3)
            assert answer.sources[0].title == "C" and answer.sources[0].citation == 1
        finally:
            for doc_id in ids:
                await store.index.delete_document(doc_id)
            await store.aclose()
            if other:
                await other.aclose()

    asyncio.run(check())
