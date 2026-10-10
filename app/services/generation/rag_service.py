from app.domain.interfaces.llm import LLM
from app.domain.models.generation import Answer
from app.services.generation.citation_service import number_sources
from app.services.generation.prompt_builder import build_prompt
from app.services.retrieval.retrieval_service import RetrievalService


class RAGService:
    def __init__(self, retrieval: RetrievalService, llm: LLM):
        self.retrieval = retrieval
        self.llm = llm

    async def ask(self, question: str, top_k: int) -> Answer:
        hits = await self.retrieval.search(question, top_k)
        completion = await self.llm.complete(build_prompt(question, hits))
        cached = (completion.usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
        return Answer(completion.text, number_sources(hits), completion.usage, cached)
