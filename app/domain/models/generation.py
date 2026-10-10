from dataclasses import dataclass
from typing import Any

from app.domain.models.chunk import SearchHit


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class Completion:
    text: str
    usage: dict[str, Any]


@dataclass(frozen=True)
class CitedHit(SearchHit):
    citation: int


@dataclass(frozen=True)
class Answer:
    answer: str
    sources: list[CitedHit]
    usage: dict[str, Any]
    cached_prompt_tokens: int
