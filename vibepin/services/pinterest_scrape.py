"""
Pinterest pin image fetcher — uses SerpAPI Google Images to find
a public profile's pin images without requiring OAuth or a browser.
"""

import re

import httpx
from fastapi import HTTPException

from vibepin.core.config import settings

_SERPAPI_URL = "https://serpapi.com/search.json"


def _normalize_username(raw: str) -> str:
    s = raw.strip().rstrip("/")
    m = re.search(r"pinterest\.\w+/([^/?#]+)", s)
    if m:
        return m.group(1)
    return s.lstrip("@").split("/")[0]


def _is_pin_image(url: str) -> bool:
    return (
        isinstance(url, str)
        and url.startswith("https://i.pinimg.com/")
        and not url.endswith((".js", ".css", ".mjs"))
    )


async def fetch_pins(profile_url_or_username: str, max_images: int = 150) -> list[dict]:
    """
    Find pin images for a public Pinterest profile via SerpAPI Google Images.
    Returns up to max_images pin dicts: {image_url, title, description, board_name}.
    """
    username = _normalize_username(profile_url_or_username)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Pinterest username or URL.")

    all_images: list[str] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Run multiple searches to gather enough images
        queries = [
            f"site:pinterest.com/{username}",
            f"pinterest.com/{username} pins fashion",
            f"pinterest {username} style outfit",
            f"pinterest.com/{username} aesthetic",
        ]

        for q in queries:
            if len(all_images) >= max_images:
                break
            params = {
                "engine": "google_images",
                "q": q,
                "num": 40,
                "api_key": settings.serpapi_key,
                "safe": "off",
            }
            try:
                r = await client.get(_SERPAPI_URL, params=params, timeout=20.0)
                if r.status_code != 200:
                    continue
                data = r.json()
                for result in data.get("images_results", []):
                    # `original` is the actual source image URL
                    for field in ("original", "thumbnail"):
                        url = result.get(field, "")
                        if _is_pin_image(url):
                            all_images.append(url)
                            break
            except Exception:
                continue

    # Deduplicate, prefer originals/736x over small thumbnails
    seen: set[str] = set()
    unique: list[str] = []
    for img in _sort_by_resolution(all_images):
        if img not in seen:
            seen.add(img)
            unique.append(img)

    return [
        {"image_url": u, "title": "", "description": "", "board_name": ""}
        for u in unique[:max_images]
    ]


_RES_ORDER = ["originals", "736x", "564x", "474x", "236x"]


def _res_rank(url: str) -> int:
    for i, seg in enumerate(_RES_ORDER):
        if f"/{seg}/" in url:
            return i
    return len(_RES_ORDER)


def _sort_by_resolution(urls: list[str]) -> list[str]:
    return sorted(urls, key=_res_rank)
