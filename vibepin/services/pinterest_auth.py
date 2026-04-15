"""
Pinterest OAuth 2.0 + API helpers.
Register your app at https://developers.pinterest.com to get credentials.
Add PINTEREST_CLIENT_ID and PINTEREST_CLIENT_SECRET to .env.
Redirect URI to register in the Pinterest dashboard: http://localhost:8000/api/vibe/callback
"""

import base64
import secrets

import httpx
from fastapi import HTTPException

from vibepin.core.config import settings

_AUTH_URL = "https://www.pinterest.com/oauth/"
_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
_API_BASE = "https://api.pinterest.com/v5"
_SCOPES = "user_accounts:read,pins:read,boards:read"
_REDIRECT_URI = "http://localhost:8000/api/vibe/callback"

# In-memory CSRF state store (single-process dev server)
_pending_states: set[str] = set()


def get_auth_url() -> str:
    state = secrets.token_urlsafe(16)
    _pending_states.add(state)
    params = (
        f"client_id={settings.pinterest_client_id}"
        f"&redirect_uri={_REDIRECT_URI}"
        f"&scope={_SCOPES}"
        f"&response_type=code"
        f"&state={state}"
    )
    return f"{_AUTH_URL}?{params}"


async def exchange_code(code: str, state: str) -> str:
    """Exchange OAuth code for access token. Returns the token string."""
    if state not in _pending_states:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state.")
    _pending_states.discard(state)

    credentials = base64.b64encode(
        f"{settings.pinterest_client_id}:{settings.pinterest_client_secret}".encode()
    ).decode()

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            _TOKEN_URL,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _REDIRECT_URI,
            },
        )
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Pinterest token exchange failed: {r.text}")

    return r.json()["access_token"]


async def fetch_pins(access_token: str, max_pins: int = 100) -> list[dict]:
    """
    Fetch up to max_pins pins from the user's boards.
    Returns list of {title, description, board_name, image_url}.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    pins: list[dict] = []

    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Get boards
        boards_r = await client.get(
            f"{_API_BASE}/boards",
            headers=headers,
            params={"page_size": 50},
        )
        if boards_r.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch Pinterest boards.")
        boards = boards_r.json().get("items", [])

        # 2. For each board, get pins
        for board in boards:
            if len(pins) >= max_pins:
                break
            board_id = board["id"]
            board_name = board.get("name", "")

            pins_r = await client.get(
                f"{_API_BASE}/boards/{board_id}/pins",
                headers=headers,
                params={
                    "page_size": min(25, max_pins - len(pins)),
                    "fields": "id,title,description,media",
                },
            )
            if pins_r.status_code != 200:
                continue

            for pin in pins_r.json().get("items", []):
                media = pin.get("media", {})
                images = media.get("images", {})
                # Try multiple sizes, prefer medium
                img_url = (
                    (images.get("400x300") or {}).get("url")
                    or (images.get("236x") or {}).get("url")
                    or (images.get("150x150") or {}).get("url")
                )
                pins.append({
                    "title": pin.get("title") or "",
                    "description": pin.get("description") or "",
                    "board_name": board_name,
                    "image_url": img_url,
                })

    return pins
