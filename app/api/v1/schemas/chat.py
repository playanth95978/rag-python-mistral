from typing import Any

from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=8)

    @field_validator("question")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La question ne peut pas être vide.")
        return value.strip()


class SourceResponse(BaseModel):
    id: str
    title: str
    text: str
    score: float
    source_id: str
    locator: str


class CitedSourceResponse(SourceResponse):
    citation: int


class SearchResponse(BaseModel):
    sources: list[SourceResponse]


class AnswerResponse(BaseModel):
    answer: str
    sources: list[CitedSourceResponse]
    usage: dict[str, Any]
    cached_prompt_tokens: int
