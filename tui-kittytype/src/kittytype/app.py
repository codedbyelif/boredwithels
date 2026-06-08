"""kittytype uygulamasi: tema kaydi, ekran kurulumu ve giris noktasi."""
from __future__ import annotations

from textual.app import App

from kittytype.screens.main_menu import MainMenuScreen
from kittytype.theme import KITTYTYPE_THEME


class KittyTypeApp(App):
    CSS_PATH = "styles/kittytype.tcss"
    TITLE = "kittytype"
    SUB_TITLE = "terminal yazma hızı testi"

    def on_mount(self) -> None:
        self.register_theme(KITTYTYPE_THEME)
        self.theme = "kittytype"
        self.push_screen(MainMenuScreen())


def main() -> None:
    KittyTypeApp().run()


if __name__ == "__main__":
    main()
