"""HTTP helpers para daily-log."""

import json
import urllib.request
from typing import Optional, Union


def fetch(url: str, headers: dict, data: Optional[bytes] = None) -> Union[dict, list]:
    """GET/POST JSON. Devuelve el body parseado o lanza excepcion."""
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def github(path: str, token: str) -> Union[dict, list]:
    return fetch(f"https://api.github.com/{path}", {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "daily-log",
    })


def shortcut(path: str, token: str) -> Union[dict, list]:
    return fetch(f"https://api.app.shortcut.com/api/v3/{path}", {
        "Shortcut-Token": token,
        "Content-Type": "application/json",
    })
