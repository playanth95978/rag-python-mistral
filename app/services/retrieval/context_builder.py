from app.domain.models.chunk import SearchHit


def build_context(hits: list[SearchHit]) -> str:
    return "\n\n".join(f"[{i}] {hit.title}\n{hit.text}" for i, hit in enumerate(hits, 1))
