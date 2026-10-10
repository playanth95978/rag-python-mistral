import math

from app.core.exceptions import InvalidEmbedding, MistralUnavailable
from app.domain.interfaces.embeddings import EmbeddingBatch
from app.infrastructure.mistral.client import MistralClient

DIMENSIONS = 1024


class MistralEmbeddingAdapter:
    def __init__(self, client: MistralClient):
        self.client = client
        self.model_name = client.settings.mistral_embed_model
        if self.model_name != "mistral-embed":
            raise ValueError("Le schéma Vespa nécessite mistral-embed (1024 dimensions).")

    async def embed(self, texts: list[str]) -> EmbeddingBatch:
        result = await self.client.post("embeddings", {"model": self.model_name, "input": texts})
        try:
            data = sorted(result["data"], key=lambda item: item["index"])
            if [item["index"] for item in data] != list(range(len(texts))):
                raise InvalidEmbedding()
            vectors = [item["embedding"] for item in data]
            if any(
                len(v) != DIMENSIONS or not all(math.isfinite(x) for x in v) or not any(x != 0 for x in v)
                for v in vectors
            ):
                raise InvalidEmbedding()
            return EmbeddingBatch(vectors, int((result.get("usage") or {}).get("total_tokens", 0)))
        except (KeyError, TypeError, ValueError):
            raise MistralUnavailable() from None
