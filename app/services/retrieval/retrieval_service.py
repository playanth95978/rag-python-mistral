from app.core.exceptions import NoDocuments
from app.domain.interfaces.vector_store import VectorStore
from app.domain.models.chunk import SearchHit


class RetrievalService:
    def __init__(self, store: VectorStore):
        self.store = store

    async def search(self, question: str, top_k: int) -> list[SearchHit]:
        hits = await self.store.search(question, top_k)
        if not hits:
            raise NoDocuments()
        return hits
