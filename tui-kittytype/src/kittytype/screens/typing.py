"""Yazma ekrani: TypingArea + StatsBar + sayac. Testi baslatir ve bitirir."""
from __future__ import annotations

import time
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from kittytype.config import Mode, TestConfig
from kittytype.core.stats import TypingStats, compute_stats
from kittytype.widgets.live_stats import StatsBar
from kittytype.widgets.typing_area import TypingArea


class TypingScreen(Screen):
    BINDINGS = [("escape", "abort", "İptal")]

    def __init__(self, text: str, config: TestConfig) -> None:
        super().__init__()
        self._text = text
        self._config = config
        self._start_time: Optional[float] = None
        self._timer = None
        self._finished = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="typing-screen"):
            yield StatsBar(
                timed=self._config.is_timed, duration=self._config.duration, id="stats"
            )
            if self._config.mode is Mode.LYRICS:
                yield Static(f"🎵  {self._config.song_title}", id="song-title")
            with Center(id="typing-center"):
                with VerticalScroll(id="typing-scroll"):
                    yield TypingArea(self._text, id="typing-area")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#typing-scroll").can_focus = False
        self.query_one(TypingArea).focus()

    @property
    def _area(self) -> TypingArea:
        return self.query_one(TypingArea)

    @property
    def _bar(self) -> StatsBar:
        return self.query_one(StatsBar)

    def on_typing_area_progress(self, message: TypingArea.Progress) -> None:
        if message.first_keystroke and self._start_time is None:
            self._start_time = time.monotonic()
            self._timer = self.set_interval(0.1, self._tick)
        self._update_stats()

    def on_typing_area_completed(self, message: TypingArea.Completed) -> None:
        self._finish()

    def _elapsed(self) -> float:
        return 0.0 if self._start_time is None else time.monotonic() - self._start_time

    def _stats(self) -> TypingStats:
        eng = self._area.engine
        return compute_stats(
            typed_count=eng.typed_count,
            correct_count=eng.correct_count,
            incorrect_count=eng.incorrect_count,
            total_keystrokes=eng.total_keystrokes,
            correct_keystrokes=eng.correct_keystrokes,
            elapsed_seconds=self._elapsed(),
        )

    def _update_stats(self) -> None:
        elapsed = self._elapsed()
        remaining = (
            max(0.0, self._config.duration - elapsed) if self._config.is_timed else 0.0
        )
        self._bar.update_live(remaining=remaining, elapsed=elapsed, stats=self._stats())

    def _tick(self) -> None:
        if self._finished:
            return
        self._update_stats()
        if self._config.is_timed and self._elapsed() >= self._config.duration:
            self._finish()

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        if self._timer is not None:
            self._timer.stop()
        self._area.freeze()
        stats = self._stats()

        from kittytype.screens.results import ResultsScreen

        self.app.switch_screen(
            ResultsScreen(stats=stats, config=self._config, text=self._text)
        )

    def action_abort(self) -> None:
        if self._timer is not None:
            self._timer.stop()
        self.app.pop_screen()

    def on_unmount(self) -> None:
        if self._timer is not None:
            self._timer.stop()
