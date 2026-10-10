from dataclasses import replace

from app.core.exceptions import InvalidEmbedding
from app.domain.interfaces.embeddings import EmbeddingProvider
from app.domain.interfaces.vector_store import VectorStore
from app.domain.models.chunk import Chunk
from app.domain.models.document import Document


class IndexingService:
    def __init__(self, embeddings: EmbeddingProvider, store: VectorStore):
        self.embeddings = embeddings
        self.store = store

    async def index(self, document: Document, chunks: list[Chunk]) -> None:
        batch = await self.embeddings.embed([chunk.text for chunk in chunks])
        if len(batch.vectors) != len(chunks):
            raise InvalidEmbedding()
        embedded = [replace(chunk, embedding=vector) for chunk, vector in zip(chunks, batch.vectors)]
        await self.store.index_document(document, embedded, batch.total_tokens)
