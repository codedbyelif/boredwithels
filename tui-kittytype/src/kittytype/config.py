"""Uygulama genelinde kullanilan secenekler ve test yapilandirmasi."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Language(str, Enum):
    TR = "tr"
    EN = "en"

    @property
    def label(self) -> str:
        return {"tr": "Türkçe", "en": "English"}[self.value]


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @property
    def label(self) -> str:
        return {"easy": "Kolay", "medium": "Orta", "hard": "Zor"}[self.value]


class Mode(str, Enum):
    RANDOM = "random"
    LYRICS = "lyrics"


# Sure secenekleri (saniye)
DURATIONS = (15, 30, 60, 120)
DEFAULT_DURATION = 30

# Rastgele modda uretilecek kelime sayisi (en uzun sureyi fazlasiyla doldurur)
RANDOM_WORD_COUNT = 400


@dataclass
class TestConfig:
    """Bir testin tum ayarlarini tasiyan kap."""

    mode: Mode
    # Rastgele kelime modu icin:
    language: Language = Language.TR
    difficulty: Difficulty = Difficulty.EASY
    duration: int = DEFAULT_DURATION
    # Sarki sozu modu icin:
    song_title: str = ""

    @property
    def is_timed(self) -> bool:
        """Geri sayim yalnizca rastgele kelime modunda vardir."""
        return self.mode is Mode.RANDOM
