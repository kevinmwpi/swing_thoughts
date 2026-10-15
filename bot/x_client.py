"""Minimal X API client: create one text post as the authenticated account."""

from __future__ import annotations

import os

from requests_oauthlib import OAuth1Session

ENV_VARS = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")

_HINTS = {
    401: "Keys or tokens are wrong. Re-copy all four into the GitHub secrets.",
    402: "Out of API credits. Top up in the X Developer Console.",
    403: (
        "Usually the access token was generated before the app was set to "
        "'Read and write'. Set the permission, then regenerate the access "
        "token and secret. Can also mean duplicate text or no credits."
    ),
    429: "Rate limited. It will work on the next run.",
}


class PostError(RuntimeError):
    pass


class XClient:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str,
                 base_url: str = "https://api.x.com"):
        self._session = OAuth1Session(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        self._base_url = base_url.rstrip("/")

    @classmethod
    def from_env(cls) -> XClient:
        missing = [name for name in ENV_VARS if not os.environ.get(name)]
        if missing:
            raise PostError(f"Missing X credentials: {', '.join(missing)}. Add them as GitHub Actions secrets.")
        return cls(*(os.environ[name] for name in ENV_VARS),
                   base_url=os.environ.get("X_API_BASE") or "https://api.x.com")

    def create_post(self, text: str) -> str:
        resp = self._session.post(f"{self._base_url}/2/tweets", json={"text": text}, timeout=30)
        return str(self._check(resp)["data"]["id"])

    def whoami(self) -> str:
        """The @username these credentials post as. Reads only; never posts."""
        resp = self._session.get(f"{self._base_url}/2/users/me", timeout=30)
        return self._check(resp)["data"]["username"]

    @staticmethod
    def _check(resp) -> dict:
        if not resp.ok:
            hint = _HINTS.get(resp.status_code, "")
            raise PostError(f"X API returned {resp.status_code}: {resp.text[:500]} {hint}".strip())
        return resp.json()
