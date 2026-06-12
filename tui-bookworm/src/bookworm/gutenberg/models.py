"""Gutendex arama sonucu modeli."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class GutenbergBook:
    """Gutendex'ten donen tek bir kitap."""

    id: int
    title: str
    authors: Tuple[str, ...]
    language: str
    download_count: int
    text_url: Optional[str]  # duz metin (.txt) adresi; yoksa standart kalip denenir

    @property
    def author(self) -> str:
        return ", ".join(self.authors)

    @property
    def display(self) -> str:
        author = self.author or "Bilinmeyen yazar"
        text = f"{self.title} — {author}"
        if self.language:
            text += f"  [{self.language}]"
        if self.download_count:
            text += f"  ({self.download_count:,} indirme)"
        return text
