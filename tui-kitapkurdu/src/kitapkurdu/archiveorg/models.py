"""Archive.org arama sonucu modeli."""
from __future__ import annotations

import zlib
from dataclasses import dataclass


@dataclass
class ArchiveBook:
    """archive.org'daki, OCR metni (DjVuTXT) bulunan bir eser."""

    identifier: str
    title: str
    creator: str = ""
    downloads: int = 0

    @property
    def book_id(self) -> int:
        return zlib.crc32(f"ia:{self.identifier}".encode("utf-8"))

    @property
    def display(self) -> str:
        text = self.title
        if self.creator:
            text += f" — {self.creator}"
        if self.downloads:
            text += f"  ({self.downloads:,} indirme)"
        return text
