from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.api.dependencies import get_services
from app.domain.models.generation import Message
from app.services.container import Services

router = APIRouter(tags=["Conversation"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=32000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_history(self):
        if self.messages[-1].role != "user":
            raise ValueError("Le dernier message doit venir de l'utilisateur.")
        if sum(len(message.content) for message in self.messages) > 200000:
            raise ValueError("Conversation trop longue. Créez une nouvelle conversation.")
        return self


@router.post("/chat")
async def chat(body: ChatRequest, services: Services = Depends(get_services)):
    if services.chat is None:
        raise HTTPException(503, "Service de conversation indisponible.")
    completion = await services.chat.reply([Message(item.role, item.content) for item in body.messages])
    return {"answer": completion.text, "model": services.chat.model, "usage": completion.usage}


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest, services: Services = Depends(get_services)):
    if services.chat is None:
        raise HTTPException(503, "Service de conversation indisponible.")
    async for chunk in services.chat.stream([Message(item.role, item.content) for item in body.messages]):
        yield {"answer": chunk.text, "model": services.chat.model, "usage": chunk.usage}
