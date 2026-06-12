"""Okuma ekrani: sayfalama, ilerleme kaydi ve klavye ile gezinme.

Metin varsayilan olarak 'akis' duzeninde gosterilir: paragraflar ekran
genisligine gore yeniden katlanir, dize bloklari korunur (bkz. reflow.py).
'f' ile kaynaktaki orijinal satir yapisina donulebilir. Ilerleme, satir
sayisindan bagimsiz kalsin diye 0-1 arasi oran olarak saklanir; pencere
boyutu ya da duzen degisince ayni orana en yakin sayfadan devam edilir.
"""
from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from kitapkurdu.library import LibraryBook
from kitapkurdu.reflow import build_lines

_MIN_WIDTH = 20
_MIN_HEIGHT = 4


class ReaderScreen(Screen):
    BINDINGS = [
        ("escape", "go_back", "Kitaplık"),
        ("right,space,pagedown,down,j", "next_page", "Sonraki"),
        ("left,pageup,up,k", "prev_page", "Önceki"),
        ("f", "toggle_flow", "Düzen"),
        ("home", "first_page", "Başa dön"),
        ("end", "last_page", "Sona git"),
    ]

    def __init__(self, book: LibraryBook) -> None:
        super().__init__()
        self.book = book
        self._lines: List[str] = []
        self._page = 0
        self._page_height = _MIN_HEIGHT
        self._flow = True  # True: akis duzeni, False: kaynaktaki satir yapisi

    def compose(self) -> ComposeResult:
        with Vertical(id="reader"):
            yield Static(self.book.display, id="reader-title")
            with Center(id="reader-center"):
                yield Static("", id="page")
            yield Static("", id="reader-status")
        yield Footer()

    def on_mount(self) -> None:
        try:
            self._text = self.app.library.read_text(self.book)
        except OSError:
            self._text = "Kitap dosyası okunamadı. (Silinmiş olabilir — kitaplıktan d ile kaldırıp tekrar indirin.)"
        self._paginate(restore_fraction=self.book.progress)

    def on_resize(self) -> None:
        if self._lines:
            self._paginate(restore_fraction=self._fraction())

    # --- Sayfalama ---

    def _fraction(self) -> float:
        """Su anki konumun 0-1 arasi orani (kaydedilen ilerleme)."""
        if not self._lines:
            return 0.0
        if self._page >= self._last_page():
            return 1.0
        return (self._page * self._page_height) / len(self._lines)

    def _last_page(self) -> int:
        if not self._lines:
            return 0
        return (len(self._lines) - 1) // self._page_height

    def _paginate(self, restore_fraction: float) -> None:
        page_widget = self.query_one("#page", Static)
        width = max(_MIN_WIDTH, page_widget.content_size.width or 0)
        self._page_height = max(_MIN_HEIGHT, page_widget.content_size.height or 0)
        self._lines = build_lines(self._text, width=width, flow=self._flow)
        # En yakin sayfa sinirina yuvarla: oran tam sinirda kaydedildigi icin
        # float hatasiyla bir onceki sayfaya dusmesin.
        target_page = round(restore_fraction * len(self._lines) / self._page_height)
        self._page = min(self._last_page(), max(0, target_page))
        self._render_page()

    def _render_page(self) -> None:
        start = self._page * self._page_height
        chunk = self._lines[start : start + self._page_height]
        self.query_one("#page", Static).update("\n".join(chunk))
        total = self._last_page() + 1
        percent = round(self._fraction() * 100)
        layout = "akış" if self._flow else "orijinal"
        self.query_one("#reader-status", Static).update(
            f"sayfa {self._page + 1}/{total}  ·  %{percent}  ·  düzen: {layout} (f)  ·  Esc kitaplık"
        )

    # --- Gezinme ---

    def _go_to(self, page: int) -> None:
        self._page = min(self._last_page(), max(0, page))
        self._render_page()
        self.app.library.update_progress(self.book, self._fraction())

    def action_next_page(self) -> None:
        self._go_to(self._page + 1)

    def action_prev_page(self) -> None:
        self._go_to(self._page - 1)

    def action_toggle_flow(self) -> None:
        fraction = self._fraction()
        self._flow = not self._flow
        self._paginate(restore_fraction=fraction)

    def action_first_page(self) -> None:
        self._go_to(0)

    def action_last_page(self) -> None:
        self._go_to(self._last_page())

    def action_go_back(self) -> None:
        self.app.library.update_progress(self.book, self._fraction())
        self.app.pop_screen()
