"""bookworm uygulamasi: tema kaydi, kitaplik ve giris noktasi."""
from __future__ import annotations

from textual.app import App

from bookworm.library import Library
from bookworm.screens.bookshelf import BookshelfScreen
from bookworm.theme import (
    BOOKWORM_LIGHT_THEME,
    BOOKWORM_NIGHT_THEME,
    BOOKWORM_SEPIA_THEME,
    BOOKWORM_THEME,
)

# Ctrl+T bu sirayla doner; secim settings.json'a yazilir
_THEME_CYCLE = ("bookworm", "bookworm-light", "bookworm-sepia", "bookworm-night")

# Uygulamanin onceki adiyla kaydedilmis tema secimleri
_LEGACY_THEMES = {
    "kitapkurdu": "bookworm",
    "kitapkurdu-light": "bookworm-light",
    "kitapkurdu-sepya": "bookworm-sepia",
    "kitapkurdu-gece": "bookworm-night",
}


class BookwormApp(App):
    CSS_PATH = "styles/bookworm.tcss"
    TITLE = "bookworm"
    SUB_TITLE = "terminal kitap okuyucu"
    BINDINGS = [("ctrl+t", "toggle_theme", "Tema")]

    def __init__(self) -> None:
        super().__init__()
        self.library = Library()

    def on_mount(self) -> None:
        self.register_theme(BOOKWORM_THEME)
        self.register_theme(BOOKWORM_LIGHT_THEME)
        self.register_theme(BOOKWORM_SEPIA_THEME)
        self.register_theme(BOOKWORM_NIGHT_THEME)
        saved = self.library.load_setting("theme")
        saved = _LEGACY_THEMES.get(saved, saved)
        self.theme = saved if saved in _THEME_CYCLE else _THEME_CYCLE[0]
        self.push_screen(BookshelfScreen())

    def action_toggle_theme(self) -> None:
        # siyah-pembe -> beyaz-pembe -> sepya -> gece -> ...
        current = self.theme if self.theme in _THEME_CYCLE else _THEME_CYCLE[0]
        index = _THEME_CYCLE.index(current)
        self.theme = _THEME_CYCLE[(index + 1) % len(_THEME_CYCLE)]
        self.library.save_setting("theme", self.theme)


def main() -> None:
    BookwormApp().run()


if __name__ == "__main__":
    main()
