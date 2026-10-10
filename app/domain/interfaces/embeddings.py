from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: list[list[float]]
    total_tokens: int


class EmbeddingProvider(Protocol):
    model_name: str

    async def embed(self, texts: list[str]) -> EmbeddingBatch: ...
