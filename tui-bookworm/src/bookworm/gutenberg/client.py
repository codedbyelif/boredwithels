"""Project Gutenberg istemcisi (async, httpx). API anahtari gerekmez.

Birincil kaynak Gutendex (https://gutendex.com, JSON). Gutendex zaman zaman
cok yavaslayip timeout verdigi icin, arama basarisiz olursa Gutenberg'in
resmi OPDS beslemesine (Atom XML) dusulur.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import List, Optional

import httpx

from bookworm import __version__
from bookworm.gutenberg.models import GutenbergBook

_GUTENDEX_URL = "https://gutendex.com/books"
_OPDS_URL = "https://www.gutenberg.org/ebooks/search.opds/"
_USER_AGENT = f"bookworm/{__version__} (https://github.com/elifkaynar)"
# Gutendex su siralar cok yavas; kisa surede yanit vermezse OPDS'ye gecilir
_GUTENDEX_TIMEOUT = 6.0
_OPDS_TIMEOUT = 20.0
_DOWNLOAD_TIMEOUT = 120.0

# Gutendex erisilemezse de calisan standart duz metin adresi kalibi
_FALLBACK_TEXT_URL = "https://www.gutenberg.org/ebooks/{id}.txt.utf-8"

_START_MARKER = "*** START OF"
_END_MARKER = "*** END OF"

_ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}
_EBOOK_ID_RE = re.compile(r"/ebooks/(\d+)")


class GutendexError(Exception):
    """Gutendex / Gutenberg ile iletisimde olusan hata."""


def _client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=timeout, headers={"User-Agent": _USER_AGENT}, follow_redirects=True
    )


# --- Gutendex (JSON) ---

def _plain_text_url(formats: dict) -> Optional[str]:
    """formats sozlugunden duz metin adresini secer (zip olanlar elenir)."""
    for mime, url in formats.items():
        if mime.startswith("text/plain") and not url.endswith(".zip"):
            return url
    return None


def _parse_book(item: dict) -> GutenbergBook:
    authors = tuple(a.get("name", "") for a in item.get("authors", []) if a.get("name"))
    languages = item.get("languages") or []
    return GutenbergBook(
        id=int(item.get("id") or 0),
        title=item.get("title") or "",
        authors=authors,
        language=", ".join(languages),
        download_count=int(item.get("download_count") or 0),
        text_url=_plain_text_url(item.get("formats") or {}),
    )


async def _gutendex_search(query: str, language: Optional[str]) -> List[GutenbergBook]:
    params = {"search": query}
    if language:
        params["languages"] = language
    async with _client(_GUTENDEX_TIMEOUT) as client:
        resp = await client.get(_GUTENDEX_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []
    return [_parse_book(item) for item in results]


# --- OPDS (Atom XML, resmi gutenberg.org) ---

def _parse_opds(xml_text: str, language: str) -> List[GutenbergBook]:
    """OPDS arama beslemesindeki kitap girislerini ayristirir."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    books = []
    for entry in root.findall("a:entry", _ATOM_NS):
        match = _EBOOK_ID_RE.search(entry.findtext("a:id", "", _ATOM_NS))
        title = (entry.findtext("a:title", "", _ATOM_NS) or "").strip()
        if not match or not title or title == "No records found.":
            continue
        author = (entry.findtext("a:content", "", _ATOM_NS) or "").strip()
        books.append(
            GutenbergBook(
                id=int(match.group(1)),
                title=title,
                authors=(author,) if author else (),
                language=language,
                download_count=0,
                text_url=None,  # indirilirken standart kalip kullanilir
            )
        )
    return books


async def _opds_search(query: str, language: Optional[str]) -> List[GutenbergBook]:
    if language:
        query = f"{query} l.{language}"
    async with _client(_OPDS_TIMEOUT) as client:
        resp = await client.get(_OPDS_URL, params={"query": query})
        resp.raise_for_status()
    return _parse_opds(resp.text, language or "")


async def search(query: str, language: Optional[str] = None) -> List[GutenbergBook]:
    """Kitap ara: once Gutendex, olmazsa resmi OPDS beslemesi.

    Iki kaynak da basarisiz olursa GutendexError firlatir.
    """
    try:
        books = await _gutendex_search(query, language)
    except (httpx.HTTPError, ValueError):
        try:
            books = await _opds_search(query, language)
        except (httpx.HTTPError, ValueError) as exc:
            raise GutendexError(str(exc)) from exc
    return [b for b in books if b.id and b.title]


# --- Metin indirme ---

def strip_boilerplate(text: str) -> str:
    """Gutenberg'in lisans basligini/sonunu ('*** START/END OF ... ***') ayiklar.

    Isaretler bulunamazsa metin oldugu gibi doner.
    """
    lines = text.splitlines()
    start, end = 0, len(lines)
    for i, line in enumerate(lines):
        if line.lstrip().startswith(_START_MARKER):
            start = i + 1
            break
    for i in range(len(lines) - 1, start, -1):
        if lines[i].lstrip().startswith(_END_MARKER):
            end = i
            break
    return "\n".join(lines[start:end]).strip("\n")


async def download(book: GutenbergBook) -> str:
    """Kitabin duz metnini indirir ve lisans kalibini ayiklayip dondurur."""
    url = book.text_url or _FALLBACK_TEXT_URL.format(id=book.id)
    try:
        async with _client(_DOWNLOAD_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise GutendexError(str(exc)) from exc
    return strip_boilerplate(resp.text)
