from app.domain.interfaces.llm import LLM
from app.domain.models.generation import Completion, Message


class ChatService:
    def __init__(self, llm: LLM, model: str):
        self.llm = llm
        self.model = model

    async def reply(self, messages: list[Message]) -> Completion:
        return await self.llm.complete(
            [
                Message(
                    "system",
                    "Tu es un assistant utile, précis et convivial. Réponds dans la langue de l'utilisateur.",
                ),
                *messages,
            ]
        )
