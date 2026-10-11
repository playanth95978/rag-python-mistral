from mistralai.search.toolkit.document import Document as ToolkitDocument
from mistralai.search.toolkit.document import DocumentChunk, DocumentChunkMetadata, DocumentMetadata
from mistralai.search.toolkit.embedding import Embedder, EmbeddingResult
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from mistralai.search.toolkit.plugins.vespa.app import VespaApp
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever
from mistralai.search.toolkit.search.errors import IndexException

from app.core.config import PROJECT_ROOT
from app.core.exceptions import ApplicationError, VectorStoreUnavailable
from app.domain.interfaces.embeddings import EmbeddingProvider
from app.domain.models.chunk import Chunk, SearchHit
from app.domain.models.document import Document


class ToolkitEmbedder(Embedder):
    """Pont entre l'interface du domaine et celle du Search Toolkit."""

    def __init__(self, provider: EmbeddingProvider):
        super().__init__(model_name=provider.model_name)
        self.provider = provider

    async def embed(self, texts, context=None) -> EmbeddingResult:
        batch = await self.provider.embed(texts)
        return EmbeddingResult(embeddings=batch.vectors, total_tokens=batch.total_tokens)


class VespaAdapter:
    def __init__(
        self, embeddings: EmbeddingProvider, endpoint: str, index=None, *, collection_name: str = "job_chunks"
    ):
        if index is None:
            app = VespaApp(PROJECT_ROOT / "vespa_app")
            index = app.get_search_index(
                VespaClientConfig(endpoint=endpoint, timeout=30), collection_name=collection_name
            )
        self.index = index
        self.embeddings = embeddings
        # Le plugin combine le texte (BM25) et l'embedding (HNSW).
        self.engine = QueryEngine(
            retriever=[VectorRetriever(client=index, embedder=ToolkitEmbedder(embeddings))]
        )

    async def index_document(self, document: Document, chunks: list[Chunk], total_tokens: int) -> None:
        converted = ToolkitDocument(
            id=document.id,
            source_id=document.source_id,
            content=document.text,
            metadata=DocumentMetadata(embed_total_tokens=total_tokens),
            chunks=[
                DocumentChunk(
                    id=chunk.id,
                    source_id=chunk.source_id,
                    locator=chunk.locator,
                    start_offset=chunk.start_offset,
                    end_offset=chunk.end_offset,
                    parent_ref=document.id,
                    content=chunk.text,
                    embedding=chunk.embedding,
                    metadata=DocumentChunkMetadata(
                        title=chunk.title, embedder_name=self.embeddings.model_name
                    ),
                )
                for chunk in chunks
            ],
        )
        try:
            await self.index.index_document(converted)
        except IndexException:
            raise VectorStoreUnavailable() from None

    async def search(self, question: str, top_k: int) -> list[SearchHit]:
        try:
            result = await self.engine.search(
                query=question, top_k=top_k, include_metadata=True, include_content=True
            )
        except RetrieverException as error:
            # Le Toolkit enveloppe aussi les erreurs du fournisseur d'embeddings.
            if isinstance(error.__cause__, ApplicationError):
                raise error.__cause__ from None
            raise VectorStoreUnavailable() from None
        return [
            SearchHit(
                id=hit.chunk.id,
                title=hit.chunk.metadata.get("title", ""),
                text=hit.chunk.content,
                score=hit.score,
                source_id=hit.chunk.source_id,
                locator=hit.chunk.locator,
            )
            for hit in result.results
        ]

    async def aclose(self) -> None:
        await self.index.aclose()
