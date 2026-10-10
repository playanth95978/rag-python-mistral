from typing import Protocol

from app.domain.models.chunk import Chunk
from app.domain.models.document import Document


class Chunker(Protocol):
    def split(self, document: Document) -> list[Chunk]: ...
