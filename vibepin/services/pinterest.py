import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

# Pinterest renders og:image server-side, so a plain GET with browser headers works.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


async def extract_image_url(pin_url: str) -> str:
    """Return the main image URL from any Pinterest pin or short-link."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            r = await client.get(pin_url, headers=_HEADERS)
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Could not fetch Pinterest page ({exc.response.status_code}).",
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=400, detail=f"Request failed: {exc}")

    soup = BeautifulSoup(r.text, "html.parser")

    for attr in ({"property": "og:image"}, {"name": "twitter:image"}):
        tag = soup.find("meta", attrs=attr)
        if tag and tag.get("content"):
            return tag["content"]

    raise HTTPException(
        status_code=422,
        detail="Could not find an image on that Pinterest URL. Make sure it's a pin, not a board.",
    )
