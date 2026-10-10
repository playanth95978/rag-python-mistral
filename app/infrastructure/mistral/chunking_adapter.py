from mistralai.search.toolkit.ingestion.text_splitters import CharacterTextSplitter

from app.domain.models.chunk import Chunk
from app.domain.models.document import Document


class MistralChunkingAdapter:
    def __init__(self, chunk_size: int = 1000):
        self.splitter = CharacterTextSplitter(chunk_size=chunk_size)

    def split(self, document: Document) -> list[Chunk]:
        return [
            Chunk(
                source_id=document.source_id,
                title=document.title,
                text=part.content,
                start_offset=part.start_offset,
                end_offset=part.end_offset,
            )
            for part in self.splitter.split_text(document.text)
        ]
