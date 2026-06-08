"""Ana menu: gercek Hello Kitty GIF'i (yoksa ASCII kedi) + mod secimi."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

# Pillow yoksa / GIF okunamazsa kullanilacak animasyonlu ASCII kedi (gozleri kirpar).
_EYES = ("o.o", "-.-", "o.o", "^.^")
_ASCII_FRAMES = ["\n".join((r" /\_/\ ", f"( {e} )", r" > ^ < ")) for e in _EYES]

_GIF_COLS = 36
_SURFACE_RGB = (0x14, 0x10, 0x14)  # $surface (kutu arka plani)


class MainMenuScreen(Screen):
    BINDINGS = [("q", "quit_app", "Çıkış")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Middle():
            with Center():
                with Vertical(id="menu"):
                    yield Center(id="cat-box")  # kedi buraya mount edilir
                    yield Static("kittytype", id="logo")
                    yield Button("⌨   Rastgele Kelimeler", id="random", variant="primary")
                    yield Button("🎵  Şarkı Sözleri", id="lyrics", variant="primary")
                    yield Button("✕   Çıkış", id="quit")
                    yield Static("coded by elif 💗", id="credit")
        yield Footer()

    def on_mount(self) -> None:
        box = self.query_one("#cat-box")
        try:
            from kittytype.widgets.gif_cat import GifCat, load_frames

            frames, intervals = load_frames(_GIF_COLS, _SURFACE_RGB)
            box.mount(GifCat(frames, intervals, id="cat"))
        except Exception:
            # Fallback: animasyonlu ASCII kedi
            box.mount(Static(_ASCII_FRAMES[0], id="cat"))
            self._ascii_i = 0
            self.set_interval(0.45, self._next_ascii)

    def _next_ascii(self) -> None:
        self._ascii_i = (self._ascii_i + 1) % len(_ASCII_FRAMES)
        self.query_one("#cat", Static).update(_ASCII_FRAMES[self._ascii_i])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "random":
            from kittytype.screens.options import OptionsScreen

            self.app.push_screen(OptionsScreen())
        elif event.button.id == "lyrics":
            from kittytype.screens.song_search import SongSearchScreen

            self.app.push_screen(SongSearchScreen())
        elif event.button.id == "quit":
            self.app.exit()

    def action_quit_app(self) -> None:
        self.app.exit()
