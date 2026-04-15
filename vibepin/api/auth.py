"""
Pinterest OAuth 2.0 flow.
GET /api/auth/pinterest          — redirect user to Pinterest login
GET /api/auth/pinterest/callback — exchange code for token, return username
"""

import urllib.parse

import httpx
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from vibepin.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

_AUTHORIZE_URL = "https://www.pinterest.com/oauth/"
_TOKEN_URL     = "https://api.pinterest.com/v5/oauth/token"
_USER_URL      = "https://api.pinterest.com/v5/user_account"
_SCOPES        = "user_accounts:read,pins:read,boards:read"


@router.get("/pinterest")
async def pinterest_login():
    client_id = settings.pinterest_client_id
    if not client_id:
        return HTMLResponse("PINTEREST_CLIENT_ID not set in .env", status_code=500)

    params = urllib.parse.urlencode({
        "client_id":     client_id,
        "redirect_uri":  settings.pinterest_redirect_uri,
        "response_type": "code",
        "scope":         _SCOPES,
    })
    return RedirectResponse(f"{_AUTHORIZE_URL}?{params}")


@router.get("/pinterest/callback")
async def pinterest_callback(code: str | None = None, error: str | None = None):
    if error or not code:
        return _close_popup(error="Pinterest login was cancelled.")

    client_id     = settings.pinterest_client_id
    client_secret = settings.pinterest_client_secret
    redirect_uri  = settings.pinterest_redirect_uri

    # Exchange code for access token
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(
            _TOKEN_URL,
            auth=(client_id, client_secret),
            data={
                "grant_type":   "authorization_code",
                "code":         code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code != 200:
            return _close_popup(error="Failed to exchange token. Please try again.")

        access_token = token_resp.json().get("access_token")
        if not access_token:
            return _close_popup(error="No access token returned.")

        # Fetch user profile
        user_resp = await client.get(
            _USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            return _close_popup(error="Could not fetch Pinterest profile.")

        user = user_resp.json()
        username = user.get("username") or user.get("id", "")

    return _close_popup(username=username)


def _close_popup(username: str = "", error: str = "") -> HTMLResponse:
    """
    Close the OAuth popup and pass the result back to the opener window.
    """
    html = f"""<!DOCTYPE html>
<html><head><title>Connecting…</title></head>
<body>
<script>
  if (window.opener) {{
    window.opener.postMessage(
      {{ type: 'pinterest_auth', username: {repr(username)}, error: {repr(error)} }},
      window.location.origin
    );
    window.close();
  }} else {{
    window.location.href = '/?pinterest_username={urllib.parse.quote(username)}';
  }}
</script>
<p style="font-family:sans-serif;padding:40px;color:#888;">Connecting… you can close this tab.</p>
</body></html>"""
    return HTMLResponse(html)
