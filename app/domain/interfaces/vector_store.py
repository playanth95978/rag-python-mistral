from typing import Protocol

from app.domain.models.chunk import Chunk, SearchHit
from app.domain.models.document import Document


class VectorStore(Protocol):
    async def index_document(self, document: Document, chunks: list[Chunk], total_tokens: int) -> None: ...

    async def search(self, question: str, top_k: int) -> list[SearchHit]: ...
