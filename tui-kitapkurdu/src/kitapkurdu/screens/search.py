"""Kitap arama ekrani: Vikikaynak, Project Gutenberg ve Archive.org kaynaklari.

Arama kutusuna http(s) ile baslayan bir adres yazilirsa arama yerine o
dosya (PDF/EPUB/TXT) dogrudan indirilip kitapliga aktarilir.
"""
from __future__ import annotations

import zlib
from typing import Union

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, ListItem, ListView, RadioButton, RadioSet, Static

from kitapkurdu import importer
from kitapkurdu.archiveorg import client as archiveorg
from kitapkurdu.archiveorg.models import ArchiveBook
from kitapkurdu.gutenberg import client as gutendex
from kitapkurdu.gutenberg.models import GutenbergBook
from kitapkurdu.wikisource import client as wikisource
from kitapkurdu.wikisource.models import WikisourceBook

AnyBook = Union[GutenbergBook, WikisourceBook, ArchiveBook]

_HINTS = {
    "wikisource": "Türkçe eserler ve serbest çeviriler (Vikikaynak) içinde arayın.",
    "gutenberg": "70.000+ kitap; orijinal/İngilizce başlık en iyi sonucu verir.",
    "archive": "Archive.org taramaları; metin OCR olduğundan kalite kitaba göre değişir.",
}
_URL_HINT = "İpucu: kutuya doğrudan bir PDF/EPUB/TXT adresi de yapıştırabilirsiniz."


class ResultItem(ListItem):
    def __init__(self, book: AnyBook) -> None:
        super().__init__(Static(book.display))
        self.book = book


class SearchScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Geri")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="search"):
            yield Static("🔍  Kitap Ara", classes="title")
            with RadioSet(id="source"):
                yield RadioButton("🇹🇷  Vikikaynak", id="src-wikisource", value=True)
                yield RadioButton("🌍  Gutenberg", id="src-gutenberg")
                yield RadioButton("📦  Archive.org", id="src-archive")
            yield Input(placeholder="Kitap / yazar ara… ya da PDF adresi yapıştır (Enter)", id="query")
            yield Static(f"{_HINTS['wikisource']} {_URL_HINT}", id="search-status")
            yield ListView(id="results")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#query", Input).focus()

    @property
    def source(self) -> str:
        pressed = self.query_one("#source", RadioSet).pressed_button
        if pressed is not None and pressed.id == "src-gutenberg":
            return "gutenberg"
        if pressed is not None and pressed.id == "src-archive":
            return "archive"
        return "wikisource"

    def _status(self, msg: str) -> None:
        self.query_one("#search-status", Static).update(msg)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self._status(_HINTS[self.source])
        self.query_one("#query", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        if query.startswith(("http://", "https://")):
            self._status(f"📥 İndiriliyor: {query[:60]}…")
            self.download_from_url(query)
        else:
            self._status("Aranıyor…")
            self.search_books(query, self.source)

    @work(exclusive=True, group="search")
    async def search_books(self, query: str, source: str) -> None:
        try:
            if source == "wikisource":
                books: list = await wikisource.search(query)
            elif source == "archive":
                books = await archiveorg.search(query)
            else:
                books = await gutendex.search(query)
        except (wikisource.WikisourceError, gutendex.GutendexError, archiveorg.ArchiveError):
            self._status("Bağlantı hatası. Tekrar deneyin.")
            return
        results = self.query_one("#results", ListView)
        await results.clear()
        if not books:
            self._status("Sonuç bulunamadı.")
            return
        self._status(f"{len(books)} sonuç — indirmek için seçin (↑↓ + Enter).")
        for book in books:
            await results.append(ResultItem(book))
        results.index = 0
        results.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, ResultItem):
            self._status(f"📥 İndiriliyor: {item.book.title}…")
            self.download_book(item.book)

    @work(exclusive=True, group="search")
    async def download_book(self, book: AnyBook) -> None:
        library = self.app.library
        if isinstance(book, WikisourceBook):
            existing = library.get(book.book_id)
            if existing is None:
                try:
                    text, author = await wikisource.download(book)
                except wikisource.WikisourceError:
                    self._status("İndirme başarısız. Tekrar deneyin.")
                    return
                existing = library.add(
                    gutenberg_id=book.book_id,
                    title=book.title,
                    author=author,
                    language="tr",
                    text=text,
                    source="wikisource",
                )
        elif isinstance(book, ArchiveBook):
            existing = library.get(book.book_id)
            if existing is None:
                try:
                    text = await archiveorg.download(book)
                except archiveorg.ArchiveError:
                    self._status("İndirme başarısız. Tekrar deneyin.")
                    return
                existing = library.add(
                    gutenberg_id=book.book_id,
                    title=book.title,
                    author=book.creator,
                    language="",
                    text=text,
                    source="archive",
                )
        else:
            existing = library.get(book.id)
            if existing is None:
                try:
                    text = await gutendex.download(book)
                except gutendex.GutendexError:
                    self._status("İndirme başarısız. Tekrar deneyin.")
                    return
                existing = library.add(
                    gutenberg_id=book.id,
                    title=book.title,
                    author=book.author,
                    language=book.language,
                    text=text,
                )
        self._open_reader(existing)

    @work(exclusive=True, group="search", thread=True)
    def download_from_url(self, url: str) -> None:
        """Indirme + PDF/EPUB cozme bloklayici oldugundan ayri is parcaciginda."""
        library = self.app.library
        book_key = zlib.crc32(f"url:{url}".encode("utf-8"))
        existing = library.get(book_key)
        if existing is None:
            try:
                title, author, text = importer.import_url(url)
            except importer.ImportFailed as exc:
                self.app.call_from_thread(self._status, f"❌ {exc}")
                return
            existing = library.add(
                gutenberg_id=book_key,
                title=title,
                author=author,
                language="",
                text=text,
                source="web",
            )
        self.app.call_from_thread(self._open_reader, existing)

    def _open_reader(self, book) -> None:
        from kitapkurdu.screens.reader import ReaderScreen

        self.app.switch_screen(ReaderScreen(book))
