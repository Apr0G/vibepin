"""
Virtual try-on via Replicate IDM-VTON.
Takes a person image and a garment image, returns the composite result URL.
"""

import asyncio
import base64
import io
import os

import httpx
from PIL import Image

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

from vibepin.core.config import settings

_MODEL = "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f"


def _u(photo_id: str, w: int = 768, h: int = 1024) -> str:
    # No crop=top so we get the full body — portrait ratio
    return f"https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&q=85"


# Full-body, front-facing, arms relaxed, neutral clothing — ideal for IDM-VTON
PRESET_MODELS = [
    {
        "id": "model_01",
        "label": "Amara",
        "url": _u("photo-1483985988355-763728e1935b"),
        "thumbnail": _u("photo-1483985988355-763728e1935b", 160, 240),
    },
    {
        "id": "model_02",
        "label": "Sofia",
        "url": _u("photo-1534528741775-53994a69daeb"),
        "thumbnail": _u("photo-1534528741775-53994a69daeb", 160, 240),
    },
    {
        "id": "model_03",
        "label": "Mia",
        "url": _u("photo-1524504388940-b1c1722653e1"),
        "thumbnail": _u("photo-1524504388940-b1c1722653e1", 160, 240),
    },
    {
        "id": "model_04",
        "label": "Zara",
        "url": _u("photo-1488161628813-04466f872be2"),
        "thumbnail": _u("photo-1488161628813-04466f872be2", 160, 240),
    },
    {
        "id": "model_05",
        "label": "Priya",
        "url": _u("photo-1531746020798-e6953c6e8e04"),
        "thumbnail": _u("photo-1531746020798-e6953c6e8e04", 160, 240),
    },
    {
        "id": "model_06",
        "label": "Luna",
        "url": _u("photo-1548142813-c348350df52b"),
        "thumbnail": _u("photo-1548142813-c348350df52b", 160, 240),
    },
    {
        "id": "model_07",
        "label": "Yuna",
        "url": _u("photo-1567721913486-6585f069b332"),
        "thumbnail": _u("photo-1567721913486-6585f069b332", 160, 240),
    },
    {
        "id": "model_08",
        "label": "Maya",
        "url": _u("photo-1596783074918-c84cb06531ca"),
        "thumbnail": _u("photo-1596783074918-c84cb06531ca", 160, 240),
    },
]


async def fetch_image_bytes(url: str, label: str = "image") -> bytes:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            url,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        if ct and not ct.startswith("image/"):
            raise ValueError(
                f"The {label} URL doesn't point to an image (got {ct.split(';')[0]}). "
                "Right-click the image and choose 'Copy image address' to get a direct image URL."
            )
        return r.content


def _to_jpeg(img_bytes: bytes, label: str = "image") -> bytes:
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        raise ValueError(
            f"Could not read the {label} file. "
            "Please upload a JPEG, PNG, or WebP image."
        )
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


async def _upload_to_imgbb(image_bytes: bytes) -> str:
    key = settings.imgbb_key
    if not key:
        raise ValueError("IMGBB_KEY not set in .env")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.imgbb.com/1/upload",
            data={"key": key, "image": b64},
        )
        resp.raise_for_status()
        return resp.json()["data"]["url"]


async def run_tryon(
    person_bytes: bytes,
    garment_bytes: bytes,
    garment_description: str = "a stylish outfit",
) -> str:
    """
    Run IDM-VTON on Replicate.
    Returns the output image URL.
    """
    import replicate

    token = settings.replicate_api_token
    if not token:
        raise ValueError("REPLICATE_API_TOKEN not set in .env")

    os.environ["REPLICATE_API_TOKEN"] = token

    person_jpeg  = _to_jpeg(person_bytes,  "person photo")
    garment_jpeg = _to_jpeg(garment_bytes, "garment photo")

    person_url, garment_url = await asyncio.gather(
        _upload_to_imgbb(person_jpeg),
        _upload_to_imgbb(garment_jpeg),
    )

    client = replicate.Client(api_token=token)
    output = await client.async_run(
        _MODEL,
        input={
            "human_img":       person_url,
            "garm_img":        garment_url,
            "garment_des":     garment_description[:200],
            "is_checked":      True,
            "is_checked_crop": True,
            "denoise_steps":   40,
            "seed":            42,
        },
    )

    if isinstance(output, list):
        result = output[0]
    else:
        result = output

    if hasattr(result, "url"):
        return str(result.url)
    return str(result)
