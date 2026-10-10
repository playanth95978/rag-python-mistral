from dataclasses import dataclass
from uuid import NAMESPACE_DNS, uuid5


@dataclass(frozen=True)
class Document:
    source_id: str
    title: str
    text: str

    @property
    def id(self) -> str:
        return str(uuid5(NAMESPACE_DNS, self.source_id))


@dataclass(frozen=True)
class IngestionResult:
    document_id: str
    chunks: int
