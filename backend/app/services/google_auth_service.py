from typing import Any, Dict

from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


class GoogleAuthError(Exception):
    pass


def verify_google_id_token(token: str) -> Dict[str, Any]:
    """Verify a Google ID token and return decoded claims."""
    if not settings.GOOGLE_CLIENT_ID:
        raise GoogleAuthError("Google sign-in is not configured on the server")

    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise GoogleAuthError("Invalid Google token") from exc

    if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise GoogleAuthError("Invalid token issuer")

    if not payload.get("sub"):
        raise GoogleAuthError("Google account ID missing from token")

    if payload.get("email_verified") is False:
        raise GoogleAuthError("Google email is not verified")

    return payload
