"""LRCLIB istemcisi (async, httpx). API anahtari gerekmez.

Belgeler: https://lrclib.net/docs
"""
from __future__ import annotations

import unicodedata
from typing import List

import httpx

from kittytype import __version__
from kittytype.lyrics.models import LrclibTrack

_BASE_URL = "https://lrclib.net/api"
_USER_AGENT = f"kittytype/{__version__} (https://github.com/elifkaynar/kittytype)"
_TIMEOUT = 10.0


class LrclibError(Exception):
    """LRCLIB ile iletisimde olusan hata."""


def _parse_track(item: dict) -> LrclibTrack:
    plain = item.get("plainLyrics")
    return LrclibTrack(
        id=int(item.get("id") or 0),
        track_name=item.get("trackName") or "",
        artist_name=item.get("artistName") or "",
        album_name=item.get("albumName") or "",
        duration=float(item.get("duration") or 0.0),
        plain_lyrics=unicodedata.normalize("NFC", plain) if plain else None,
        instrumental=bool(item.get("instrumental")),
    )


async def search(query: str) -> List[LrclibTrack]:
    """Sarki ara; sozu olan (enstrumantal olmayan) sonuclari dondurur.

    Aglar/timeout/gecersiz yanit durumunda LrclibError firlatir.
    """
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT}
        ) as client:
            resp = await client.get(f"{_BASE_URL}/search", params={"q": query})
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise LrclibError(str(exc)) from exc

    if not isinstance(data, list):
        return []
    tracks = [_parse_track(item) for item in data]
    return [t for t in tracks if not t.instrumental and t.plain_lyrics]
