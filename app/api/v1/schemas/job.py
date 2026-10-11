from datetime import datetime

from pydantic import BaseModel


class JobOfferResponse(BaseModel):
    source: str
    source_id: str | None
    title: str
    description: str
    company: str | None
    location: str | None
    country: str | None
    apply_url: str | None
    contract_type: str | None
    salary_min: int | None
    salary_max: int | None
    published_at: datetime | None
    remote: bool


class JobIngestionRequest(BaseModel):
    keywords: str | None = None
    location: str | None = None
    country: str | None = None
    sources: list[str] | None = None


class JobIngestionResponse(BaseModel):
    fetched: int
    indexed: int
    chunks: int
    failed: int
