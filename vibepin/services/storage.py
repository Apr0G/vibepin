import base64

import httpx
from fastapi import HTTPException

from vibepin.core.config import settings

_IMGBB_URL = "https://api.imgbb.com/1/upload"


async def upload(image_bytes: bytes) -> str:
    """Upload raw image bytes to imgbb and return the public URL."""
    b64 = base64.b64encode(image_bytes).decode()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(
                _IMGBB_URL,
                params={"key": settings.imgbb_key},
                data={"image": b64},
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Image hosting failed ({exc.response.status_code}). Check your IMGBB_KEY.",
            )

    body = r.json()
    if not body.get("success"):
        raise HTTPException(status_code=502, detail="imgbb returned an error.")

    return body["data"]["url"]
