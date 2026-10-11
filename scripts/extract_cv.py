from pathlib import Path
import asyncio

from app.core.config import Settings
from app.domain.interfaces.embeddings import EmbeddingBatch
from app.domain.models.document import Document
from app.infrastructure.mistral.client import MistralClient
from app.infrastructure.mistral.embedding_adapter import MistralEmbeddingAdapter

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
    text:str = extract_text(Path("scripts/cv.txt"))
    chunks:list[str] = chunk_text(text, chunk_size=500)

    client:MistralClient = MistralClient(Settings())
    documents = []

    try:
        adapter:MistralEmbeddingAdapter = MistralEmbeddingAdapter(client)
        batch: EmbeddingBatch = await adapter.embed(chunks)

        for index, (chunk, vector) in enumerate(zip(chunks, batch.vectors, strict=True)):
            print(f'index:{index}\tchunk:{len(chunk)}\tvector:{len(vector)}')
            document = {
                'id': f"cv-{index}",
                'text': chunk,
                'embedding': vector,
            }
            documents.append(document)

        print(documents[0]["id"])
        print(documents[0]["text"][:80])
        print(len(documents[0]["embedding"]))
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
