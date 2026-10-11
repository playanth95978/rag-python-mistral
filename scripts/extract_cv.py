import asyncio
from pathlib import Path

from app.core.config import Settings
from app.domain.interfaces.embeddings import EmbeddingBatch
from app.domain.models.chunk import Chunk
from app.domain.models.document import Document
from app.infrastructure.mistral.client import MistralClient
from app.infrastructure.mistral.embedding_adapter import MistralEmbeddingAdapter
from app.infrastructure.vector_store.vespa_adapter import VespaAdapter

path: Path = Path("scripts/cv.txt")


def extract_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        print('chunk', i, chunk)
        chunks.append(chunk)

    return chunks


async def main():
    text: str = extract_text(Path("scripts/cv.txt"))
    chunks: list[str] = chunk_text(text, chunk_size=500)

    client: MistralClient = MistralClient(Settings())

    try:
        adapter: MistralEmbeddingAdapter = MistralEmbeddingAdapter(client)
        batch: EmbeddingBatch = await adapter.embed(chunks)

        cv: Document = Document(
            source_id="cv-demo",
            title="Mon CV",
            text=text,
        )

        vespa_chunks: list[Chunk] = []
        offset: int = 0

        for chunk, vector in zip(chunks, batch.vectors, strict=True):
            vespa_chunks.append(
                Chunk(
                    source_id=cv.source_id,
                    title=cv.title,
                    text=chunk,
                    start_offset=offset,
                    end_offset=offset + len(chunk),
                    embedding=vector,
                )
            )
            offset += len(chunk)

        print(vespa_chunks[0].locator)
        store: VespaAdapter = VespaAdapter(
            embeddings=adapter,
            endpoint=Settings().vespa_url,
            collection_name="cv_user",
        )
        try:
            await store.index_document(document=cv, chunks=vespa_chunks, total_tokens=batch.total_tokens)
            print(f"CV indexé dans cv_user : {len(vespa_chunks)} morceaux")
        finally:
            await store.aclose()
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
