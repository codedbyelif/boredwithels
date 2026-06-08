"""Hedef metne karsi yazma durumunu tutan saf (UI'siz) motor."""
from __future__ import annotations

from enum import Enum
from typing import List


class CharStatus(Enum):
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"


def matches(typed: str, target: str) -> bool:
    """Yazilan karakter hedefe uyuyor mu?

    Yeni satir hedefi (satir sonu) bosluk veya Enter ile gecilebilir.
    """
    if target == "\n":
        return typed in (" ", "\n")
    return typed == target


class TypingEngine:
    """Hedef metin + yazilan tampon + her pozisyon icin durum.

    Turkce notu: karsilastirma her zaman tam (case-sensitive) kod noktasi
    esitligidir - asla .lower() kullanilmaz (Turkce buyuk/kucuk donusumu bozuktur).
    """

    def __init__(self, target: str) -> None:
        self.target = target
        self.typed: List[str] = []        # yazilan karakterler (backspace ile kisalir)
        self.total_keystrokes = 0         # basilan tum karakter tuslari (duzeltilenler dahil)
        self.correct_keystrokes = 0       # basildigi anda dogru olan tuslar

    # --- girdi ---
    def type_char(self, ch: str) -> None:
        if self.is_complete:
            return
        pos = len(self.typed)
        self.typed.append(ch)
        self.total_keystrokes += 1
        if pos < len(self.target) and matches(ch, self.target[pos]):
            self.correct_keystrokes += 1

    def backspace(self) -> None:
        if self.typed:
            self.typed.pop()

    # --- durum ---
    @property
    def cursor(self) -> int:
        return len(self.typed)

    @property
    def is_complete(self) -> bool:
        return len(self.typed) >= len(self.target)

    def status_at(self, index: int) -> CharStatus:
        if index >= len(self.typed):
            return CharStatus.PENDING
        if index < len(self.target) and matches(self.typed[index], self.target[index]):
            return CharStatus.CORRECT
        return CharStatus.INCORRECT

    @property
    def typed_count(self) -> int:
        return len(self.typed)

    @property
    def correct_count(self) -> int:
        return sum(
            1
            for i, ch in enumerate(self.typed)
            if i < len(self.target) and matches(ch, self.target[i])
        )

    @property
    def incorrect_count(self) -> int:
        return self.typed_count - self.correct_count
