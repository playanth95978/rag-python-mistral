import httpx
from fastapi.testclient import TestClient

from app.api.v1.routers.vespa_admin import get_explorer
from app.core.config import Settings
from app.infrastructure.vector_store.vespa_explorer import VespaExplorer
from app.main import create_app
from app.services.container import Services


def test_explorer_browse_detail_and_read_only_contract():
    requests = []

    def handler(request):
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(
                200, json={"fields": {"content": "Python", "content_embedding": {"values": [1, 0]}}}
            )
        return httpx.Response(
            200,
            json={
                "root": {
                    "fields": {"totalCount": 1},
                    "children": [
                        {
                            "fields": {
                                "id": "chunk-1",
                                "content": "Python",
                                "documentid": "id:cv_user:cv_user::chunk-1",
                            }
                        }
                    ],
                }
            },
        )

    upstream = httpx.AsyncClient(base_url="http://vespa.test", transport=httpx.MockTransport(handler))
    app = create_app(Services(None, None, None), Settings(_env_file=None))
    app.dependency_overrides[get_explorer] = lambda: VespaExplorer(upstream)
    with TestClient(app) as client:
        assert client.get("/admin/vespa").status_code == 200
        assert client.get("/static/vespa.js").status_code == 200
        base = "/api/v1/admin/vespa"
        assert len(client.get(base + "/collections").json()["collections"]) == 2
        result = client.get(base + "/cv_user/documents", params={"query": "Python", "offset": 20})
        assert result.status_code == 200
        assert result.json()["offset"] == 20
        detail = client.get(base + "/cv_user/documents/chunk-1")
        assert detail.json()["fields"]["content_embedding"]["values"] == [1, 0]
        assert client.get(base + "/unknown/documents").status_code == 422
        assert client.get(base + "/cv_user/documents?offset=-1").status_code == 422
        assert client.get(base + "/cv_user/documents?limit=9999").status_code == 422
        assert client.delete(base + "/cv_user/documents/chunk-1").status_code == 405
    assert requests[-1].url.path == "/document/v1/cv_user/cv_user/docid/chunk-1"


def test_explorer_handles_upstream_outage():
    upstream = httpx.AsyncClient(
        base_url="http://vespa.test",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(500, text="private upstream diagnostics")
        ),
    )
    app = create_app(Services(None, None, None), Settings(_env_file=None))
    app.dependency_overrides[get_explorer] = lambda: VespaExplorer(upstream)
    with TestClient(app) as client:
        result = client.get("/api/v1/admin/vespa/cv_user/documents")
        assert result.status_code == 503
        assert "private" not in result.text
