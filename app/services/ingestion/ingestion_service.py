from uuid import uuid4

from app.domain.interfaces.chunking import Chunker
from app.domain.models.document import Document, IngestionResult
from app.services.ingestion.indexing_service import IndexingService


class IngestionService:
    def __init__(self, chunker: Chunker, indexing: IndexingService):
        self.chunker = chunker
        self.indexing = indexing

    async def ingest(self, title: str, text: str) -> IngestionResult:
        return await self.ingest_document(Document(source_id=str(uuid4()), title=title, text=text))

    async def ingest_document(self, document: Document) -> IngestionResult:
        chunks = self.chunker.split(document)
        await self.indexing.index(document, chunks)
        return IngestionResult(document_id=document.id, chunks=len(chunks))
