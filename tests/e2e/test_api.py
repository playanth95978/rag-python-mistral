from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.exceptions import NoDocuments, VectorStoreUnavailable
from app.domain.models.chunk import SearchHit
from app.domain.models.document import IngestionResult
from app.main import create_app
from app.services.container import Services
from app.services.generation.chat_service import ChatService
from app.services.generation.rag_service import RAGService
from app.services.retrieval.retrieval_service import RetrievalService
from tests.fakes import FakeLLM


def test_conversation_preserves_history_without_retrieval():
    llm = FakeLLM()
    services = Services(None, None, None, ChatService(llm, "mistral-large-4"))
    with TestClient(create_app(services, Settings(_env_file=None))) as client:
        assert client.get("/").status_code == 200
        assert client.get("/static/chat.js").status_code == 200
        history = [
            {"role": "user", "content": "Je m'appelle Alice."},
            {"role": "assistant", "content": "Bonjour Alice !"},
            {"role": "user", "content": "Quel est mon prénom ?"},
        ]
        result = client.post("/api/v1/chat", json={"messages": history})
        assert result.status_code == 200
        assert result.json()["model"] == "mistral-large-4"
        assert llm.messages[0].role == "system"
        assert [message.content for message in llm.messages[1:]] == [item["content"] for item in history]
        assert client.post("/api/v1/chat", json={"messages": []}).status_code == 422
        assert (
            client.post("/api/v1/chat", json={"messages": [{"role": "system", "content": "x"}]}).status_code
            == 422
        )
        assert client.post("/api/v1/chat", json={"messages": history[:-1]}).status_code == 422


@pytest.mark.parametrize("prefix", ["/api/v1", ""])
def test_http_contract_and_legacy_routes(prefix):
    hit = SearchHit("chunk1", "A", "Python", 1, "source", "char:0-6")
    store = SimpleNamespace(search=AsyncMock(return_value=[]))
    retrieval = RetrievalService(store)
    services = Services(
        SimpleNamespace(ingest=AsyncMock(return_value=IngestionResult("doc1", 1))),
        retrieval,
        RAGService(retrieval, FakeLLM()),
    )
    with TestClient(create_app(services, Settings(_env_file=None))) as client:
        assert client.get(prefix + "/health").json() == {"status": "ok"}
        assert client.post(prefix + "/ask", json={"question": "Python ?"}).status_code == 404
        assert client.post(prefix + "/documents", json={"title": "A", "text": "Python"}).status_code == 201
        store.search.return_value = [hit]
        result = client.post(prefix + "/ask", json={"question": "Python ?", "top_k": 1})
        assert result.status_code == 200
        assert result.json()["sources"][0]["citation"] == 1
        assert result.json()["cached_prompt_tokens"] == 64
        assert (
            client.post(prefix + "/search", json={"question": "Python ?"}).json()["sources"][0]["id"]
            == "chunk1"
        )
        assert client.post(prefix + "/search", json={"question": "Python ?", "top_k": 0}).status_code == 422
        assert client.post(prefix + "/documents", json={"title": "A", "text": "   "}).status_code == 422
        paths = client.get("/openapi.json").json()["paths"]
        assert "/api/v1/ask" in paths and "/ask" not in paths


def test_errors_are_translated_only_at_http_boundary():
    services = Services(
        SimpleNamespace(ingest=AsyncMock(side_effect=VectorStoreUnavailable())),
        SimpleNamespace(search=AsyncMock(side_effect=NoDocuments())),
        SimpleNamespace(ask=AsyncMock(side_effect=NoDocuments())),
    )
    with TestClient(create_app(services, Settings(_env_file=None))) as client:
        result = client.post("/api/v1/documents", json={"title": "A", "text": "Python"})
        assert result.status_code == 503
        assert result.json()["detail"] == VectorStoreUnavailable.detail
