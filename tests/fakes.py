from app.domain.interfaces.embeddings import EmbeddingBatch
from app.domain.models.generation import Completion


class FakeEmbeddings:
    model_name = "mistral-embed"

    async def embed(self, texts):
        return EmbeddingBatch(
            [[1, 0] + [0] * 1022 if "Python" in text else [0, 1] + [0] * 1022 for text in texts],
            total_tokens=len(texts) * 5,
        )


class FakeLLM:
    def __init__(self):
        self.messages = []

    async def complete(self, messages):
        self.messages = messages
        return Completion("Python est demandé [1].", {"prompt_tokens_details": {"cached_tokens": 64}})
