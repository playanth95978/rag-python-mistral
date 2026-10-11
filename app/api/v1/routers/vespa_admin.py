from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.infrastructure.vector_store.vespa_explorer import VespaExplorer

router = APIRouter(prefix="/admin/vespa", tags=["Explorateur Vespa"])
Collection = Literal["job_chunks", "cv_user"]


def get_explorer(request: Request) -> VespaExplorer:
    return request.app.state.vespa_explorer


@router.get("/collections")
async def collections(explorer: VespaExplorer = Depends(get_explorer)):
    return {"collections": await explorer.collections()}


@router.get("/{collection}/documents")
async def documents(
    collection: Collection,
    query: str = Query("", max_length=500),
    offset: int = Query(0, ge=0, le=1000),
    limit: int = Query(20, ge=1, le=50),
    explorer: VespaExplorer = Depends(get_explorer),
):
    return await explorer.browse(collection, query.strip(), offset, limit)


@router.get("/{collection}/documents/{chunk_id}")
async def detail(
    collection: Collection,
    chunk_id: str,
    explorer: VespaExplorer = Depends(get_explorer),
):
    if len(chunk_id) > 200:
        raise HTTPException(422, "Identifiant trop long")
    document = await explorer.detail(collection, chunk_id)
    if document is None:
        raise HTTPException(404, "Morceau introuvable")
    return document
