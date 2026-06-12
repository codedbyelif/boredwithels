"""Yerel dosya acma ekrani: PDF/EPUB/TXT secip kitapliga aktarir."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer, Header, Static

from bookworm import importer


class BookFileTree(DirectoryTree):
    """Sadece klasorleri ve desteklenen kitap dosyalarini gosterir."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            p
            for p in paths
            if not p.name.startswith(".")
            and (p.is_dir() or p.suffix.lower() in importer.SUPPORTED_EXTENSIONS)
        ]


class FileOpenScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Geri")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="file-open"):
            yield Static("📂  Dosya Aç — PDF · EPUB · TXT", classes="title")
            yield Static(
                "Bir dosya seçin; metni çıkarılıp kitaplığa eklenir.", id="file-status"
            )
            yield BookFileTree(Path.home(), id="file-tree")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#file-tree", BookFileTree).focus()

    def _status(self, msg: str) -> None:
        self.query_one("#file-status", Static).update(msg)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self._status(f"📥 Aktarılıyor: {event.path.name}…")
        self.import_book(event.path)

    @work(exclusive=True, thread=True)
    def import_book(self, path: Path) -> None:
        """pypdf/zip cozme islemleri bloklayici oldugu icin ayri is parcaciginda calisir."""
        library = self.app.library
        book = library.get(importer.book_id_for(path))
        if book is None:
            try:
                title, author, text = importer.import_file(path)
            except importer.ImportFailed as exc:
                self.app.call_from_thread(self._status, f"❌ {exc}")
                return
            book = library.add(
                gutenberg_id=importer.book_id_for(path),
                title=title,
                author=author,
                language="",
                text=text,
                source="local",
            )
        self.app.call_from_thread(self._open_reader, book)

    def _open_reader(self, book) -> None:
        from bookworm.screens.reader import ReaderScreen

        self.app.switch_screen(ReaderScreen(book))
