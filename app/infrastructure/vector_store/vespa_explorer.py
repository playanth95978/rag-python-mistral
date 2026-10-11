import json
from urllib.parse import quote

import httpx

from app.core.exceptions import VectorStoreUnavailable

COLLECTIONS = {"job_chunks": "Offres d’emploi", "cv_user": "CV utilisateurs"}


class VespaExplorer:
    """Exploration en lecture seule, sans génération ni appel embeddings."""

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = await self.client.request(method, path, **kwargs)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict) or data.get("root", {}).get("errors"):
                raise ValueError("Réponse Vespa invalide")
            return data
        except (httpx.HTTPError, ValueError):
            raise VectorStoreUnavailable() from None

    async def browse(self, collection: str, query: str = "", offset: int = 0, limit: int = 20) -> dict:
        if collection not in COLLECTIONS:
            raise ValueError("Collection inconnue")
        condition = '({defaultIndex:"content"}userInput(@query))' if query else "true"
        result = await self.request(
            "POST",
            "/search/",
            json={
                "yql": f"select * from {collection} where {condition}",
                "query": query,
                "ranking": "unranked",
                "hits": limit,
                "offset": offset,
            },
        )
        root = result.get("root", {})
        return {
            "collection": collection,
            "total": root.get("fields", {}).get("totalCount", 0),
            "offset": offset,
            "limit": limit,
            "items": [hit.get("fields", {}) for hit in root.get("children", [])],
            "coverage": root.get("coverage", {}),
        }

    async def collections(self) -> list[dict]:
        result = []
        for name, label in COLLECTIONS.items():
            page = await self.browse(name, limit=0)
            result.append({"name": name, "label": label, "chunks": page["total"]})
        return result

    async def detail(self, collection: str, chunk_id: str) -> dict | None:
        if collection not in COLLECTIONS:
            raise ValueError("Collection inconnue")
        result = await self.request(
            "POST",
            "/search/",
            json={
                "yql": f"select * from {collection} where id contains {json.dumps(chunk_id)}",
                "ranking": "unranked",
                "hits": 1,
            },
        )
        hits = result.get("root", {}).get("children", [])
        if not hits:
            return None
        fields = hits[0]["fields"]
        parts = fields["documentid"].split(":", 4)
        if len(parts) != 5 or parts[0] != "id" or parts[2] != collection or parts[3]:
            raise VectorStoreUnavailable()
        path = f"/document/v1/{quote(parts[1], safe='')}/{collection}/docid/{quote(parts[4], safe='')}"
        return await self.request("GET", path)
