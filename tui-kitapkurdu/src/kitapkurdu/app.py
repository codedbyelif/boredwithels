"""kitapkurdu uygulamasi: tema kaydi, kitaplik ve giris noktasi."""
from __future__ import annotations

from textual.app import App

from kitapkurdu.library import Library
from kitapkurdu.screens.bookshelf import BookshelfScreen
from kitapkurdu.theme import (
    KITAPKURDU_LIGHT_THEME,
    KITAPKURDU_NIGHT_THEME,
    KITAPKURDU_SEPIA_THEME,
    KITAPKURDU_THEME,
)

# Ctrl+T bu sirayla doner; secim settings.json'a yazilir
_THEME_CYCLE = ("kitapkurdu", "kitapkurdu-light", "kitapkurdu-sepya", "kitapkurdu-gece")


class KitapKurduApp(App):
    CSS_PATH = "styles/kitapkurdu.tcss"
    TITLE = "kitapkurdu"
    SUB_TITLE = "terminal kitap okuyucu"
    BINDINGS = [("ctrl+t", "toggle_theme", "Tema")]

    def __init__(self) -> None:
        super().__init__()
        self.library = Library()

    def on_mount(self) -> None:
        self.register_theme(KITAPKURDU_THEME)
        self.register_theme(KITAPKURDU_LIGHT_THEME)
        self.register_theme(KITAPKURDU_SEPIA_THEME)
        self.register_theme(KITAPKURDU_NIGHT_THEME)
        saved = self.library.load_setting("theme")
        self.theme = saved if saved in _THEME_CYCLE else _THEME_CYCLE[0]
        self.push_screen(BookshelfScreen())

    def action_toggle_theme(self) -> None:
        # siyah-pembe -> beyaz-pembe -> sepya -> gece -> ...
        current = self.theme if self.theme in _THEME_CYCLE else _THEME_CYCLE[0]
        index = _THEME_CYCLE.index(current)
        self.theme = _THEME_CYCLE[(index + 1) % len(_THEME_CYCLE)]
        self.library.save_setting("theme", self.theme)


def main() -> None:
    KitapKurduApp().run()


if __name__ == "__main__":
    main()
