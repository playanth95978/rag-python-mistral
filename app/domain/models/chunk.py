from dataclasses import dataclass
from uuid import NAMESPACE_DNS, uuid5


@dataclass(frozen=True)
class Chunk:
    source_id: str
    title: str
    text: str
    start_offset: int
    end_offset: int
    embedding: list[float] | None = None

    @property
    def locator(self) -> str:
        return f"char:{self.start_offset}-{self.end_offset}"

    @property
    def id(self) -> str:
        return str(uuid5(NAMESPACE_DNS, f"{self.source_id}:{self.locator}"))


@dataclass(frozen=True)
class SearchHit:
    id: str
    title: str
    text: str
    score: float
    source_id: str
    locator: str
