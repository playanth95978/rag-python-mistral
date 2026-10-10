from typing import Protocol

from app.domain.models.generation import Completion, Message


class LLM(Protocol):
    async def complete(self, messages: list[Message]) -> Completion: ...
