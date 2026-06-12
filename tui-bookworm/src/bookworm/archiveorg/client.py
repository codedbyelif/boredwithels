"""Archive.org istemcisi (async, httpx). API anahtari gerekmez.

Sadece OCR metni (DjVuTXT) olan eserler aranir; indirirken dosya adi
metadata API'sinden bulunur (tanimlayiciyla ayni olmayabilir). OCR metni
taramadan geldigi icin kalitesi kitaptan kitaba degisir; hafif bir
temizlik (tireyle bolunmus satirlar, cift bosluklar) uygulanir.
"""
from __future__ import annotations

import re
from typing import List, Union

import httpx

from bookworm import __version__
from bookworm.archiveorg.models import ArchiveBook

_SEARCH_URL = "https://archive.org/advancedsearch.php"
_METADATA_URL = "https://archive.org/metadata/{identifier}"
_DOWNLOAD_URL = "https://archive.org/download/{identifier}/{name}"
_USER_AGENT = f"bookworm/{__version__} (https://github.com/elifkaynar)"
_SEARCH_TIMEOUT = 30.0
_DOWNLOAD_TIMEOUT = 180.0

_HYPHEN_BREAK_RE = re.compile(r"(\w)-\s*\n\s*(\w)")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")


class ArchiveError(Exception):
    """Archive.org ile iletisimde olusan hata."""


def _client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=timeout, headers={"User-Agent": _USER_AGENT}, follow_redirects=True
    )


def _join(value: Union[str, list, None]) -> str:
    """Arama alanlari tek deger ya da liste gelebilir."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value) if value else ""


def _parse_docs(docs: List[dict]) -> List[ArchiveBook]:
    books = []
    for doc in docs:
        identifier = doc.get("identifier") or ""
        title = _join(doc.get("title"))
        if not identifier or not title:
            continue
        books.append(
            ArchiveBook(
                identifier=identifier,
                title=title,
                creator=_join(doc.get("creator")),
                downloads=int(doc.get("downloads") or 0),
            )
        )
    return books


async def search(query: str) -> List[ArchiveBook]:
    """OCR metni olan eserleri arar (alaka sirasiyla)."""
    params = {
        "q": f"({query}) AND mediatype:(texts) AND format:(DjVuTXT)",
        "fl[]": ["identifier", "title", "creator", "downloads"],
        "rows": "30",
        "output": "json",
    }
    try:
        async with _client(_SEARCH_TIMEOUT) as client:
            resp = await client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ArchiveError(str(exc)) from exc
    docs = data.get("response", {}).get("docs", [])
    return _parse_docs(docs if isinstance(docs, list) else [])


def clean_ocr(text: str) -> str:
    """OCR metnindeki tireyle bolunmus kelimeleri birlestirir, fazla boslugu kirpar."""
    text = _HYPHEN_BREAK_RE.sub(r"\1\2", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip("\n")


async def download(book: ArchiveBook) -> str:
    """Eserin OCR metnini indirir; once metadata'dan dosya adi bulunur."""
    try:
        async with _client(_DOWNLOAD_TIMEOUT) as client:
            resp = await client.get(_METADATA_URL.format(identifier=book.identifier))
            resp.raise_for_status()
            files = resp.json().get("files", [])
            names = [f.get("name", "") for f in files if f.get("name", "").endswith("_djvu.txt")]
            if not names:
                raise ArchiveError(f"'{book.identifier}' için OCR metni bulunamadı")
            resp = await client.get(
                _DOWNLOAD_URL.format(identifier=book.identifier, name=names[0])
            )
            resp.raise_for_status()
    except (httpx.HTTPError, ValueError) as exc:
        raise ArchiveError(str(exc)) from exc
    return clean_ocr(resp.text)
