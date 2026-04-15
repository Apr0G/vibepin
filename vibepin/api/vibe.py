from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vibepin.services import pinterest_scrape, vibe_analyze, vibe_recommend

router = APIRouter(prefix="/api/vibe", tags=["vibe"])

# Simple in-memory cache: username → analyzed profile
_cache: dict[str, dict] = {}


# ── Response models ───────────────────────────────────────────────────────────

class VibeProfile(BaseModel):
    scores: dict[str, float]
    top_styles: list[str]
    pin_count: int


class RecommendResponse(BaseModel):
    results: list[dict]
    top_styles: list[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/debug", summary="Debug vibe pipeline step by step")
async def debug(username: str):
    import asyncio
    from vibepin.services import clip_model

    key = pinterest_scrape._normalize_username(username)
    out: dict = {"username": key}

    # Step 1: scrape pins
    try:
        pins = await pinterest_scrape.fetch_pins(username)
        out["pin_count"] = len(pins)
        out["sample_urls"] = [p["image_url"] for p in pins[:5]]
    except Exception as e:
        out["scrape_error"] = str(e)
        return out

    # Step 2: download one image
    if pins:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(pins[0]["image_url"], follow_redirects=True)
            out["first_image_status"] = r.status_code
            out["first_image_bytes"] = len(r.content)
        except Exception as e:
            out["download_error"] = str(e)

    # Step 3: encode one image with CLIP (expose real error)
    if pins:
        import httpx
        from vibepin.services.clip_model import _encode_image_sync
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(pins[0]["image_url"], follow_redirects=True)
            import asyncio, concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as ex:
                vec = await loop.run_in_executor(ex, _encode_image_sync, r.content)
            out["clip_vector_shape"] = list(vec.shape) if vec is not None else None
        except Exception as e:
            out["clip_error"] = str(e)

    # Step 4: encode archetype text (expose real error)
    try:
        from vibepin.services.clip_model import _encode_text_sync
        import asyncio, concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as ex:
            vec = await loop.run_in_executor(ex, _encode_text_sync, "quiet luxury minimal neutral outfit")
        out["text_vector_shape"] = list(vec.shape) if vec is not None else None
    except Exception as e:
        out["text_encode_error"] = str(e)

    return out


@router.get("/analyze", response_model=VibeProfile, summary="Analyse a public Pinterest profile with CLIP")
async def analyze(username: str):
    """
    Pass a Pinterest username or full profile URL.
    e.g. /api/vibe/analyze?username=pinterest.com/someone
    """
    key = pinterest_scrape._normalize_username(username)

    if key in _cache:
        c = _cache[key]
        return VibeProfile(scores=c["scores"], top_styles=c["top_styles"], pin_count=c["pin_count"])

    pins = await pinterest_scrape.fetch_pins(username)
    if not pins:
        raise HTTPException(status_code=404, detail="No images found. Make sure the profile is public and has boards.")

    scores = await vibe_analyze.analyze_pins(pins)
    if not scores:
        raise HTTPException(
            status_code=500,
            detail="CLIP analysis returned nothing. The model may still be loading — try again in a moment.",
        )

    top_styles = [s for s, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]]
    _cache[key] = {"scores": scores, "top_styles": top_styles, "pin_count": len(pins)}

    return VibeProfile(scores=scores, top_styles=top_styles, pin_count=len(pins))


@router.get("/recommend", response_model=RecommendResponse, summary="Get recommendations for a vibe profile")
async def recommend(username: str):
    key = pinterest_scrape._normalize_username(username)
    if key not in _cache:
        raise HTTPException(status_code=400, detail="Run /api/vibe/analyze first.")

    cached = _cache[key]
    results = await vibe_recommend.recommend(cached["scores"])
    return RecommendResponse(results=results, top_styles=cached["top_styles"])
