"""Rastgele kelime modu ayarlari: dil, zorluk, sure."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, RadioButton, RadioSet, Static

from kittytype.config import (
    DEFAULT_DURATION,
    DURATIONS,
    Difficulty,
    Language,
    Mode,
    TestConfig,
)


class OptionsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Geri")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Middle():
            with Center():
                with Vertical(id="options"):
                    yield Static("⌨  Rastgele Kelimeler", classes="title")
                    yield Label("Dil")
                    with RadioSet(id="lang"):
                        yield RadioButton("Türkçe", value=True, id="lang-tr")
                        yield RadioButton("English", id="lang-en")
                    yield Label("Zorluk")
                    with RadioSet(id="diff"):
                        yield RadioButton("Kolay", value=True, id="diff-easy")
                        yield RadioButton("Orta", id="diff-medium")
                        yield RadioButton("Zor", id="diff-hard")
                    yield Label("Süre")
                    with RadioSet(id="dur"):
                        for d in DURATIONS:
                            yield RadioButton(
                                f"{d} sn", value=(d == DEFAULT_DURATION), id=f"dur-{d}"
                            )
                    with Horizontal(id="options-actions"):
                        yield Button("Başla", id="start", variant="primary")
                        yield Button("Geri", id="back")
        yield Footer()

    def _selected(self, set_id: str) -> str:
        rs = self.query_one(f"#{set_id}", RadioSet)
        return rs.pressed_button.id if rs.pressed_button else ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
            return
        if event.button.id != "start":
            return

        language = Language.EN if self._selected("lang") == "lang-en" else Language.TR
        difficulty = {
            "diff-easy": Difficulty.EASY,
            "diff-medium": Difficulty.MEDIUM,
            "diff-hard": Difficulty.HARD,
        }.get(self._selected("diff"), Difficulty.EASY)
        dur_id = self._selected("dur")
        duration = int(dur_id.split("-")[1]) if dur_id else DEFAULT_DURATION
        config = TestConfig(
            mode=Mode.RANDOM,
            language=language,
            difficulty=difficulty,
            duration=duration,
        )

        from kittytype.core.text_source import build_random_text
        from kittytype.screens.typing import TypingScreen

        text = build_random_text(language, difficulty)
        self.app.switch_screen(TypingScreen(text=text, config=config))
