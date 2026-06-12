"""Yerel dosyalardan (PDF, EPUB, TXT/MD) kitap ice aktarma.

Hepsi duz metne cevrilip kitapliga normal kitap gibi yazilir; okuyucu icin
fark yoktur. Taranmis (resim) PDF'lerde cikarilacak metin olmadigindan
ImportFailed firlatilir.
"""
from __future__ import annotations

import posixpath
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path
from typing import Tuple

import httpx

from bookworm.wikisource.client import html_to_text

SUPPORTED_EXTENSIONS = (".pdf", ".epub", ".txt", ".md")

_URL_TIMEOUT = 180.0
_SUFFIX_BY_TYPE = {
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
}

_CONTAINER_NS = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
_OPF_NS = {"o": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}


class ImportFailed(Exception):
    """Dosya okunamadi ya da icinden metin cikarilamadi."""


def book_id_for(path: Path) -> int:
    """Dosya yolu icin kararli kitaplik anahtari."""
    return zlib.crc32(str(path.resolve()).encode("utf-8"))


def import_file(path: Path) -> Tuple[str, str, str]:
    """Dosyayi duz metne cevirir; (baslik, yazar, metin) dondurur."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        title, author, text = _from_pdf(path)
    elif suffix == ".epub":
        title, author, text = _from_epub(path)
    elif suffix in (".txt", ".md"):
        title, author, text = path.stem, "", _read_text(path)
    else:
        raise ImportFailed(f"Desteklenmeyen dosya türü: {suffix}")
    if not text.strip():
        raise ImportFailed("Dosyadan metin çıkarılamadı (taranmış PDF olabilir).")
    return title or path.stem, author, text


def import_url(url: str) -> Tuple[str, str, str]:
    """URL'deki PDF/EPUB/TXT dosyasini indirip duz metne cevirir (senkron).

    Dosya turu once adres yolundaki uzantidan, yoksa Content-Type'tan anlasilir.
    """
    try:
        with httpx.Client(timeout=_URL_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ImportFailed(f"İndirilemedi: {exc}") from exc
    name = Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).name or "indirilen"
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        ctype = (resp.headers.get("content-type") or "").split(";")[0].strip().lower()
        suffix = _SUFFIX_BY_TYPE.get(ctype, ".txt" if ctype.startswith("text/") else "")
        if not suffix:
            raise ImportFailed(f"Desteklenmeyen içerik türü: {ctype or 'bilinmiyor'}")
    with tempfile.TemporaryDirectory() as tmp:
        # gecici dosya URL'deki adi tasir ki basliksiz dosyalarda baslik anlamli olsun
        path = Path(tmp) / (Path(name).stem + suffix)
        path.write_bytes(resp.content)
        return import_file(path)


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        # Eski Turkce metin dosyalari icin Windows-1254
        return raw.decode("cp1254", errors="replace")


def _from_pdf(path: Path) -> Tuple[str, str, str]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        if reader.is_encrypted:
            reader.decrypt("")  # bos parolali sifreleme yaygindir
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        meta = reader.metadata
    except Exception as exc:
        raise ImportFailed(f"PDF okunamadı: {exc}") from exc
    title = (meta.title or "").strip() if meta else ""
    author = (meta.author or "").strip() if meta else ""
    return title, author, "\n\n".join(p for p in pages if p)


def _from_epub(path: Path) -> Tuple[str, str, str]:
    try:
        with zipfile.ZipFile(path) as zf:
            container = ET.fromstring(zf.read("META-INF/container.xml"))
            rootfile = container.find(".//c:rootfile", _CONTAINER_NS)
            opf_path = rootfile.get("full-path") if rootfile is not None else None
            if not opf_path:
                raise ImportFailed("EPUB içinde içerik dosyası (OPF) bulunamadı.")
            opf = ET.fromstring(zf.read(opf_path))
            title = (opf.findtext(".//dc:title", "", _OPF_NS) or "").strip()
            author = (opf.findtext(".//dc:creator", "", _OPF_NS) or "").strip()
            manifest = {
                item.get("id"): item.get("href")
                for item in opf.findall(".//o:manifest/o:item", _OPF_NS)
            }
            base = posixpath.dirname(opf_path)
            parts = []
            for ref in opf.findall(".//o:spine/o:itemref", _OPF_NS):
                href = manifest.get(ref.get("idref"))
                if not href:
                    continue
                name = posixpath.normpath(posixpath.join(base, href))
                try:
                    html = zf.read(name).decode("utf-8", errors="replace")
                except KeyError:
                    continue
                text = html_to_text(html)
                if text:
                    parts.append(text)
    except ImportFailed:
        raise
    except (zipfile.BadZipFile, ET.ParseError, KeyError, OSError) as exc:
        raise ImportFailed(f"EPUB okunamadı: {exc}") from exc
    return title, author, "\n\n\n".join(parts)
