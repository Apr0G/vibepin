"""
Try-on API endpoints.
POST /api/tryon/run  — run virtual try-on
GET  /api/tryon/models — list preset models
"""

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from vibepin.services import moderation, tryon

router = APIRouter(prefix="/api/tryon", tags=["tryon"])


@router.get("/models")
async def get_models():
    return {"models": tryon.PRESET_MODELS}


@router.post("/run")
async def run_tryon(
    # Person: either an uploaded file OR a preset model ID
    person_file: UploadFile | None = File(default=None),
    person_model_id: str | None = Form(default=None),
    # Garment: either an uploaded file OR a URL
    garment_file: UploadFile | None = File(default=None),
    garment_url: str | None = Form(default=None),
    garment_description: str = Form(default="a stylish outfit"),
):
    # ── Resolve person image ──────────────────────────────────────────────────
    if person_file is not None:
        person_bytes = await person_file.read()
        if len(person_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Person photo must be under 10 MB.")
    elif person_model_id:
        model = next((m for m in tryon.PRESET_MODELS if m["id"] == person_model_id), None)
        if not model:
            raise HTTPException(400, "Unknown preset model ID.")
        person_bytes = await tryon.fetch_image_bytes(model["url"])
    else:
        raise HTTPException(400, "Provide either a person photo or a preset model ID.")

    # ── Resolve garment image ─────────────────────────────────────────────────
    if garment_file is not None:
        garment_bytes = await garment_file.read()
        if len(garment_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Garment photo must be under 10 MB.")
    elif garment_url:
        try:
            garment_bytes = await tryon.fetch_image_bytes(garment_url, "garment")
        except ValueError as e:
            raise HTTPException(400, str(e))
        except Exception:
            raise HTTPException(400, "Could not fetch the garment URL. Make sure it's a direct link to an image.")
    else:
        raise HTTPException(400, "Provide either a garment photo or a garment URL.")

    # ── Safety checks ─────────────────────────────────────────────────────────
    # Skip moderation for preset models (they're pre-vetted)
    if person_file is not None:
        safe, reason = await moderation.check_person_photo(person_bytes)
        if not safe:
            raise HTTPException(400, reason)

    safe, reason = await moderation.check_garment_photo(garment_bytes)
    if not safe:
        raise HTTPException(400, reason)

    # ── Run try-on ────────────────────────────────────────────────────────────
    try:
        result_url = await tryon.run_tryon(person_bytes, garment_bytes, garment_description)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"Try-on failed: {str(e)}")

    return {"result_url": result_url}
