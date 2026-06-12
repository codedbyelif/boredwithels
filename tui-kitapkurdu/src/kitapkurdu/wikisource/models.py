"""Vikikaynak arama sonucu modeli."""
from __future__ import annotations

import zlib
from dataclasses import dataclass


@dataclass
class WikisourceBook:
    """tr.wikisource.org'daki bir eser (sayfa ya da alt sayfali kitap)."""

    title: str
    wordcount: int = 0  # alt sayfa hitlerinde bilinmez (0 = gosterme)

    @property
    def book_id(self) -> int:
        """Kitaplik icin kararli sayisal anahtar (Gutenberg id'leriyle cakismaz denecek kadar genis)."""
        return zlib.crc32(self.title.encode("utf-8"))

    @property
    def display(self) -> str:
        if self.wordcount:
            return f"{self.title}  (~{self.wordcount:,} kelime)"
        return self.title
