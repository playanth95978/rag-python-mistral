import asyncio
import json

import httpx
import pytest

from app.core.config import Settings
from app.core.exceptions import InvalidEmbedding, MissingCredentials, MistralTimeout, MistralUnavailable
from app.domain.models.generation import Message
from app.infrastructure.mistral.client import MistralClient
from app.infrastructure.mistral.embedding_adapter import MistralEmbeddingAdapter
from app.infrastructure.mistral.llm_adapter import MistralLLMAdapter


def settings(**values):
    return Settings(_env_file=None, mistral_api_key="fake-test-key", **values)


def test_large4_content_blocks_and_greedy_sampling():
    def handler(request):
        payload = json.loads(request.content)
        assert payload["model"] == "mistral-large-4"
        assert payload["top_p"] == 1
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"type": "thinking", "thinking": [{"type": "text", "text": "internal"}]},
                                {"type": "text", "text": "Salut !"},
                            ]
                        }
                    }
                ]
            },
        )

    async def check():
        client = MistralClient(settings(), httpx.MockTransport(handler))
        try:
            result = await MistralLLMAdapter(client, "mistral-large-4", 4096).complete(
                [Message("user", "Salut")]
            )
            assert result.text == "Salut !"
        finally:
            await client.aclose()

    asyncio.run(check())


def test_wire_format_and_embedding_order():
    requests = []

    def handler(request):
        payload = json.loads(request.content)
        requests.append((request.url.path, payload))
        assert request.headers["authorization"] == "Bearer fake-test-key"
        if request.url.path.endswith("/embeddings"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {"index": 1, "embedding": [0, 1] + [0] * 1022},
                        {"index": 0, "embedding": [1, 0] + [0] * 1022},
                    ],
                    "usage": {"total_tokens": 9},
                },
            )
        return httpx.Response(200, json={"choices": [{"message": {"content": "OK"}}]})

    async def check():
        client = MistralClient(settings(), httpx.MockTransport(handler))
        try:
            batch = await MistralEmbeddingAdapter(client).embed(["Python", "Java"])
            assert [vector[:2] for vector in batch.vectors] == [[1, 0], [0, 1]]
            assert batch.total_tokens == 9
            result = await MistralLLMAdapter(client).complete([Message("user", "Question ?")])
            assert result.text == "OK"
        finally:
            await client.aclose()

    asyncio.run(check())
    assert requests[0][1]["input"] == ["Python", "Java"]
    assert requests[1][1]["prompt_cache_key"] == "mini-job-rag-v1"
    assert requests[1][1]["messages"][-1]["content"] == "Question ?"


@pytest.mark.parametrize("vector", [[1, 0], [0] * 1024, [float("inf")] * 1024])
def test_invalid_vectors(vector):
    async def check():
        # Utilisation d'un client factice : JSON standard refuse Infinity.
        from types import SimpleNamespace
        from unittest.mock import AsyncMock

        client = SimpleNamespace(
            settings=settings(), post=AsyncMock(return_value={"data": [{"index": 0, "embedding": vector}]})
        )
        with pytest.raises(InvalidEmbedding):
            await MistralEmbeddingAdapter(client).embed(["bad"])

    asyncio.run(check())


@pytest.mark.parametrize(
    "mode,expected",
    [("quota", MistralUnavailable), ("timeout", MistralTimeout), ("json", MistralUnavailable)],
)
def test_upstream_errors_do_not_expose_payload(mode, expected):
    def handler(request):
        if mode == "timeout":
            raise httpx.ReadTimeout("secret provider diagnostics", request=request)
        if mode == "json":
            return httpx.Response(200, text="not-json")
        return httpx.Response(429, text="secret provider diagnostics")

    async def check():
        client = MistralClient(settings(), httpx.MockTransport(handler))
        try:
            with pytest.raises(expected) as error:
                await client.post("embeddings", {})
            assert "secret" not in error.value.detail
        finally:
            await client.aclose()

    asyncio.run(check())


def test_missing_key_does_not_send_request(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    def handler(request):
        pytest.fail("Aucun appel réseau attendu.")

    async def check():
        client = MistralClient(Settings(_env_file=None, mistral_api_key=""), httpx.MockTransport(handler))
        try:
            with pytest.raises(MissingCredentials):
                await client.post("embeddings", {})
        finally:
            await client.aclose()

    asyncio.run(check())
