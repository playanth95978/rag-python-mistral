from dataclasses import asdict

from app.domain.models.chunk import SearchHit
from app.domain.models.generation import CitedHit


def number_sources(hits: list[SearchHit]) -> list[CitedHit]:
    """Numérotation alignée sur le prompt ; ne valide pas les affirmations du modèle."""
    return [CitedHit(**asdict(hit), citation=i) for i, hit in enumerate(hits, 1)]
