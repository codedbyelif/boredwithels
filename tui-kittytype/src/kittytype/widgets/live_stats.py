"""Canli istatistik cubugu: sure, WPM, dogruluk."""
from __future__ import annotations

from typing import Optional

from rich.text import Text
from textual.widget import Widget

from kittytype.core.stats import TypingStats


class StatsBar(Widget):
    def __init__(self, timed: bool, duration: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._timed = timed
        self._duration = duration
        self._remaining = float(duration)
        self._elapsed = 0.0
        self._stats: Optional[TypingStats] = None

    def update_live(
        self, *, remaining: float, elapsed: float, stats: TypingStats
    ) -> None:
        self._remaining = remaining
        self._elapsed = elapsed
        self._stats = stats
        self.refresh()

    def render(self) -> Text:
        if self._timed:
            time_part = f"⏱  {max(0, int(round(self._remaining)))} sn"
        else:
            time_part = f"⏱  {int(self._elapsed)} sn"
        wpm = self._stats.gross_wpm if self._stats else 0.0
        acc = self._stats.accuracy if self._stats else 100.0
        return Text(f"{time_part}      ⌨  {wpm:.0f} WPM      ✓  {acc:.0f}%")
