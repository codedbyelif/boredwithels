"""WPM ve dogruluk hesaplari (saf fonksiyonlar, UI'dan bagimsiz)."""
from __future__ import annotations

from dataclasses import dataclass


def _minutes(elapsed_seconds: float) -> float:
    return elapsed_seconds / 60.0


def gross_wpm(typed_chars: int, elapsed_seconds: float) -> float:
    """Brut WPM = (yazilan karakter / 5) / dakika. 5 karakter = 1 'kelime'."""
    if elapsed_seconds <= 0 or typed_chars <= 0:
        return 0.0
    return (typed_chars / 5.0) / _minutes(elapsed_seconds)


def net_wpm(typed_chars: int, uncorrected_errors: int, elapsed_seconds: float) -> float:
    """Net WPM = brut - (duzeltilmemis hata / dakika), 0'in altina dusmez."""
    if elapsed_seconds <= 0:
        return 0.0
    gross = gross_wpm(typed_chars, elapsed_seconds)
    penalty = uncorrected_errors / _minutes(elapsed_seconds)
    return max(0.0, gross - penalty)


def accuracy(correct_keystrokes: int, total_keystrokes: int) -> float:
    """Dogruluk % = dogru tus / toplam tus (duzeltilenler dahil her tus sayilir)."""
    if total_keystrokes <= 0:
        return 100.0
    return correct_keystrokes / total_keystrokes * 100.0


@dataclass
class TypingStats:
    gross_wpm: float
    net_wpm: float
    accuracy: float
    elapsed_seconds: float
    raw_chars: int          # basilan tum tuslar (duzeltilenler dahil)
    correct_chars: int      # su an hedefe gore dogru karakter sayisi
    incorrect_chars: int    # su an yanlis karakter sayisi


def compute_stats(
    *,
    typed_count: int,
    correct_count: int,
    incorrect_count: int,
    total_keystrokes: int,
    correct_keystrokes: int,
    elapsed_seconds: float,
) -> TypingStats:
    return TypingStats(
        gross_wpm=gross_wpm(typed_count, elapsed_seconds),
        net_wpm=net_wpm(typed_count, incorrect_count, elapsed_seconds),
        accuracy=accuracy(correct_keystrokes, total_keystrokes),
        elapsed_seconds=elapsed_seconds,
        raw_chars=total_keystrokes,
        correct_chars=correct_count,
        incorrect_chars=incorrect_count,
    )
