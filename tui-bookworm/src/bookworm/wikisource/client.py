"""Vikikaynak (tr.wikisource.org) istemcisi: Turkce eserler ve serbest ceviriler.

MediaWiki API kullanilir. Icerik `action=parse` ile render edilmis HTML olarak
alinir (cogu eser taranmis sayfa aktarimiyla geldigi icin `extracts` bos doner),
sonra basit bir ayristiriciyla duz metne cevrilir.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import List

import httpx

from bookworm import __version__
from bookworm.wikisource.models import WikisourceBook

_API_URL = "https://tr.wikisource.org/w/api.php"
_USER_AGENT = f"bookworm/{__version__} (https://github.com/elifkaynar)"
_TIMEOUT = 30.0

# Bu siniflari tasiyan elemanlar metne alinmaz: baslik sablonu, gezinme,
# taranmis sayfa numaralari, duzenleme linkleri vb.
_SKIP_CLASS_RE = re.compile(
    r"ws-noexport|noprint|pagenum|mw-editsection|searchaux|sisitem|navigation|metadata"
)
_BLOCK_TAGS = {"p", "div", "li", "tr", "table", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"}
_VOID_TAGS = {"br", "hr", "img", "wbr", "meta", "link", "input", "source"}

_AUTHOR_RE = re.compile(r'class="fn">([^<]+)<')


class WikisourceError(Exception):
    """Vikikaynak ile iletisimde olusan hata."""


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT}, follow_redirects=True
    )


async def _api(client: httpx.AsyncClient, **params) -> dict:
    params.update(format="json", formatversion="2")
    try:
        resp = await client.get(_API_URL, params=params)
        resp.raise_for_status()
        return resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise WikisourceError(str(exc)) from exc


# --- HTML -> duz metin ---

class _TextExtractor(HTMLParser):
    """Atlanacak elemanlarin tum alt agacini sayarak duz metin toplar."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _VOID_TAGS:
            if tag == "br" and not self._skip_depth:
                self.parts.append("\n")
            return
        if self._skip_depth:
            self._skip_depth += 1
            return
        attrd = dict(attrs)
        cls = attrd.get("class") or ""
        style = (attrd.get("style") or "").replace(" ", "")
        if tag in ("style", "script") or _SKIP_CLASS_RE.search(cls) or "display:none" in style:
            self._skip_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _VOID_TAGS:
            return
        if self._skip_depth:
            self._skip_depth -= 1
            return
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip("\n")


def _natural_key(title: str):
    """'Bölüm 10' 'Bölüm 2'den sonra gelsin diye sayilari sayi olarak karsilastirir."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", title)]


# --- Arama ---

def _collapse_results(items: List[dict]) -> List[WikisourceBook]:
    """Alt sayfa hitlerini ('Kitap/Bölüm 3') kok esere indirger ve yinelenenleri eler."""
    books: List[WikisourceBook] = []
    seen = set()
    for item in items:
        title = item.get("title") or ""
        if not title:
            continue
        root = title.split("/")[0]
        if root in seen:
            continue
        seen.add(root)
        wordcount = int(item.get("wordcount") or 0) if root == title else 0
        books.append(WikisourceBook(title=root, wordcount=wordcount))
    return books


async def search(query: str) -> List[WikisourceBook]:
    """Eser ara; alt sayfa sonuclarini kok kitaba indirgenmis halde dondurur."""
    async with _client() as client:
        data = await _api(
            client, action="query", list="search", srsearch=query, srnamespace="0", srlimit="30"
        )
    items = data.get("query", {}).get("search", [])
    return _collapse_results(items if isinstance(items, list) else [])


# --- Indirme ---

async def _subpages(client: httpx.AsyncClient, title: str) -> List[str]:
    data = await _api(
        client, action="query", list="prefixsearch", pssearch=f"{title}/", pslimit="200"
    )
    found = [p.get("title", "") for p in data.get("query", {}).get("prefixsearch", [])]
    return sorted((t for t in found if t.startswith(f"{title}/")), key=_natural_key)


async def _page_html(client: httpx.AsyncClient, title: str) -> str:
    data = await _api(client, action="parse", page=title, prop="text")
    return data.get("parse", {}).get("text", "") or ""


def extract_author(html: str) -> str:
    match = _AUTHOR_RE.search(html)
    return match.group(1).strip() if match else ""


async def download(book: WikisourceBook) -> "tuple[str, str]":
    """Eserin tum metnini indirir: (metin, yazar) dondurur.

    Ana sayfa + dogal sirali alt sayfalar birlestirilir; bolum basliklari
    alt sayfa adindan eklenir.
    """
    async with _client() as client:
        pages = [book.title] + await _subpages(client, book.title)
        parts: List[str] = []
        author = ""
        for page in pages:
            html = await _page_html(client, page)
            if not author:
                author = extract_author(html)
            text = html_to_text(html)
            if not text:
                continue
            if page != book.title:
                heading = page.split("/", 1)[1]
                parts.append(f"{heading}\n\n{text}")
            else:
                parts.append(text)
    full = "\n\n\n".join(parts).strip()
    if not full:
        raise WikisourceError(f"'{book.title}' sayfasinda okunabilir metin bulunamadi")
    return full, author
