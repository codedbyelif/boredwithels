"""Sonuc ekrani: net/brut WPM, dogruluk, sure, karakter; tekrar / menu / cikis."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from kittytype.config import Mode, TestConfig
from kittytype.core.stats import TypingStats


class ResultsScreen(Screen):
    BINDINGS = [
        ("r", "retry", "Tekrar"),
        ("m", "menu", "Ana Menü"),
        ("escape", "menu", "Ana Menü"),
        ("q", "quit_app", "Çıkış"),
    ]

    def __init__(self, stats: TypingStats, config: TestConfig, text: str) -> None:
        super().__init__()
        self._stats = stats
        self._config = config
        self._text = text

    def _card(self, value: str, label: str, big: bool = False) -> Vertical:
        return Vertical(
            Static(value, classes="stat-value"),
            Static(label, classes="stat-label"),
            classes="stat-card big" if big else "stat-card",
        )

    def compose(self) -> ComposeResult:
        s = self._stats
        yield Header(show_clock=False)
        with Middle():
            with Center():
                with Vertical(id="results-panel"):
                    yield Static("🏁  Sonuçlar", classes="title")
                    with Horizontal(classes="stat-row"):
                        yield self._card(f"{s.net_wpm:.0f}", "Net WPM", big=True)
                        yield self._card(f"{s.accuracy:.0f}%", "Doğruluk", big=True)
                    with Horizontal(classes="stat-row"):
                        yield self._card(f"{s.gross_wpm:.0f}", "Brüt WPM")
                        yield self._card(f"{s.elapsed_seconds:.0f} sn", "Süre")
                        yield self._card(str(s.raw_chars), "Karakter")
                    with Horizontal(id="results-actions"):
                        yield Button("Tekrar (R)", id="retry", variant="primary")
                        yield Button("Ana Menü (M)", id="menu")
                        yield Button("Çıkış (Q)", id="quit")
        yield Footer()

    def action_retry(self) -> None:
        from kittytype.core.text_source import build_random_text
        from kittytype.screens.typing import TypingScreen

        if self._config.mode is Mode.RANDOM:
            text = build_random_text(self._config.language, self._config.difficulty)
        else:
            text = self._text
        self.app.switch_screen(TypingScreen(text=text, config=self._config))

    def action_menu(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        handlers = {
            "retry": self.action_retry,
            "menu": self.action_menu,
            "quit": self.action_quit_app,
        }
        handler = handlers.get(event.button.id)
        if handler is not None:
            handler()
