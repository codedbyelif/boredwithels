"""Kitaplik ekrani (ana menu): indirilen kitaplar + ilerleme yuzdeleri."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ListItem, ListView, Static

from bookworm.library import LibraryBook

_EMPTY_HINT = "Kitaplığın boş. 🔍 ile Project Gutenberg'den kitap ara!"


class BookItem(ListItem):
    def __init__(self, book: LibraryBook) -> None:
        super().__init__(Static(book.display))
        self.book = book


class BookshelfScreen(Screen):
    BINDINGS = [
        ("s", "open_search", "Kitap Ara"),
        ("o", "open_file", "Dosya Aç"),
        ("d", "delete_book", "Sil"),
        ("q", "quit_app", "Çıkış"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="shelf"):
            yield Static("📚  bookworm", id="logo")
            yield Static("terminalde kitap oku", id="tagline")
            yield Static(_EMPTY_HINT, id="shelf-status")
            yield ListView(id="shelf-list")
            yield Button("🔍  Kitap Ara (Vikikaynak · Gutenberg)", id="search", variant="primary")
            yield Button("📂  Dosya Aç (PDF · EPUB · TXT)", id="open-file", variant="primary")
            yield Static("coded by elif 💗", id="credit")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_shelf()

    def on_screen_resume(self) -> None:
        # Okuyucudan donunce ilerleme yuzdeleri guncellensin
        self.refresh_shelf()

    def refresh_shelf(self) -> None:
        shelf = self.query_one("#shelf-list", ListView)
        shelf.clear()
        books = self.app.library.sorted_books()
        status = self.query_one("#shelf-status", Static)
        if not books:
            status.update(_EMPTY_HINT)
            return
        status.update(f"{len(books)} kitap — açmak için seçin (↑↓ + Enter), silmek için d.")
        for book in books:
            shelf.append(BookItem(book))
        shelf.index = 0
        shelf.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, BookItem):
            from bookworm.screens.reader import ReaderScreen

            self.app.push_screen(ReaderScreen(item.book))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search":
            self.action_open_search()
        elif event.button.id == "open-file":
            self.action_open_file()

    def action_open_search(self) -> None:
        from bookworm.screens.search import SearchScreen

        self.app.push_screen(SearchScreen())

    def action_open_file(self) -> None:
        from bookworm.screens.file_open import FileOpenScreen

        self.app.push_screen(FileOpenScreen())

    def action_delete_book(self) -> None:
        shelf = self.query_one("#shelf-list", ListView)
        item = shelf.highlighted_child
        if isinstance(item, BookItem):
            self.app.library.remove(item.book)
            self.refresh_shelf()

    def action_quit_app(self) -> None:
        self.app.exit()
