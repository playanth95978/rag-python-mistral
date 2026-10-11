from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class JobOffer:
    source: str
    source_id: str | None
    title: str
    description: str
    company: str | None = None
    location: str | None = None
    country: str | None = None
    apply_url: str | None = None
    contract_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    published_at: datetime | None = None
    remote: bool = False
