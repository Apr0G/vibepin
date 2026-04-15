from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

import vibepin.core.cache as cache
from vibepin.services import lens, pinterest, storage

router = APIRouter(prefix="/api/find", tags=["find"])

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB


# ── Response models ───────────────────────────────────────────────────────────

class ResultItem(BaseModel):
    title: str
    link: str
    source: str
    thumbnail: str
    price: str | None


class FindResponse(BaseModel):
    results: list[ResultItem]
    image_url: str = ""   # the image that was searched — shown as preview in UI
    cached: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=FindResponse, summary="Find from screenshot")
async def find_from_upload(file: UploadFile = File(...)):
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Use JPEG, PNG, or WEBP.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > _MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum is 10 MB.")

    key = cache.image_key(image_bytes)
    if hit := cache.get(key):
        return FindResponse(results=hit["results"], image_url=hit["image_url"], cached=True)

    image_url = await storage.upload(image_bytes)
    results = await lens.search(image_url)

    cache.set(key, {"results": results, "image_url": image_url})
    return FindResponse(results=results, image_url=image_url)


@router.post("/debug/url", summary="Raw SerpAPI response (dev only)")
async def debug_url(body: dict):
    url: str = (body.get("url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="'url' field is required.")
    image_url = await pinterest.extract_image_url(url)
    return await lens.raw(image_url)


@router.post("/url", response_model=FindResponse, summary="Find from Pinterest URL")
async def find_from_url(body: dict):
    url: str = (body.get("url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="'url' field is required.")

    key = cache.url_key(url)
    if hit := cache.get(key):
        return FindResponse(results=hit["results"], image_url=hit["image_url"], cached=True)

    image_url = await pinterest.extract_image_url(url)
    results = await lens.search(image_url)

    cache.set(key, {"results": results, "image_url": image_url})
    return FindResponse(results=results, image_url=image_url)
