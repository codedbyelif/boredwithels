"""Yerel kitaplik: indirilen kitaplar + okuma ilerlemesi (~/.bookworm altinda JSON)."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class LibraryBook:
    """Kitapliktaki tek bir kitabin kaydi."""

    gutenberg_id: int       # yerel benzersiz anahtar (Vikikaynak icin baslik crc32'si)
    title: str
    author: str
    language: str
    progress: float = 0.0   # 0.0 - 1.0 arasi, kalinan yerin orani
    last_read: float = 0.0  # epoch; kitaplik bu alana gore siralanir
    source: str = "gutenberg"  # "gutenberg" | "wikisource"

    @property
    def percent(self) -> int:
        return round(self.progress * 100)

    @property
    def display(self) -> str:
        text = self.title
        if self.author:
            text += f" — {self.author}"
        return f"{text}  ·  %{self.percent}"


class Library:
    """library.json'u yukler/kaydeder, kitap metin dosyalarini yonetir."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path.home() / ".bookworm"
            legacy = Path.home() / ".kitapkurdu"
            # Uygulamanin onceki adindan tek seferlik veri tasima
            if legacy.is_dir() and not data_dir.exists():
                legacy.rename(data_dir)
        self.data_dir = data_dir
        self.books_dir = self.data_dir / "books"
        self.file = self.data_dir / "library.json"
        self.settings_file = self.data_dir / "settings.json"
        self.books: List[LibraryBook] = self._load()

    def _load(self) -> List[LibraryBook]:
        try:
            data = json.loads(self.file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        if not isinstance(data, list):
            return []
        books = []
        for item in data:
            try:
                books.append(LibraryBook(**item))
            except TypeError:
                continue
        return books

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file.write_text(
            json.dumps([asdict(b) for b in self.books], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def path_for(self, book: LibraryBook) -> Path:
        return self.books_dir / f"{book.gutenberg_id}.txt"

    def get(self, gutenberg_id: int) -> Optional[LibraryBook]:
        for book in self.books:
            if book.gutenberg_id == gutenberg_id:
                return book
        return None

    def sorted_books(self) -> List[LibraryBook]:
        """En son okunan en ustte."""
        return sorted(self.books, key=lambda b: b.last_read, reverse=True)

    def add(
        self,
        gutenberg_id: int,
        title: str,
        author: str,
        language: str,
        text: str,
        source: str = "gutenberg",
    ) -> LibraryBook:
        """Kitabi diske yazip kitapliga ekler; zaten varsa mevcut kaydi dondurur."""
        existing = self.get(gutenberg_id)
        if existing is not None:
            return existing
        book = LibraryBook(
            gutenberg_id=gutenberg_id, title=title, author=author, language=language, source=source
        )
        self.books_dir.mkdir(parents=True, exist_ok=True)
        self.path_for(book).write_text(text, encoding="utf-8")
        self.books.append(book)
        self.save()
        return book

    def update_progress(self, book: LibraryBook, progress: float) -> None:
        book.progress = min(1.0, max(0.0, progress))
        book.last_read = time.time()
        self.save()

    def remove(self, book: LibraryBook) -> None:
        try:
            self.path_for(book).unlink()
        except OSError:
            pass
        self.books = [b for b in self.books if b.gutenberg_id != book.gutenberg_id]
        self.save()

    def read_text(self, book: LibraryBook) -> str:
        return self.path_for(book).read_text(encoding="utf-8")

    # --- Kucuk ayarlar (tema vb.) ---

    def _load_settings(self) -> dict:
        try:
            data = json.loads(self.settings_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def load_setting(self, key: str, default=None):
        return self._load_settings().get(key, default)

    def save_setting(self, key: str, value) -> None:
        settings = self._load_settings()
        settings[key] = value
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file.write_text(
            json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
        )
