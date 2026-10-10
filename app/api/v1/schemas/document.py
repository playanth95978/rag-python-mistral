from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=30000)

    @field_validator("title", "text")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Le texte ne peut pas être vide.")
        return value.strip()


class DocumentResponse(BaseModel):
    document_id: str
    chunks: int
