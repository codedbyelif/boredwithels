"""LRCLIB sonuc modeli."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class LrclibTrack:
    id: int
    track_name: str
    artist_name: str
    album_name: str
    duration: float
    plain_lyrics: Optional[str]
    instrumental: bool

    @property
    def display(self) -> str:
        """Liste ogesinde gosterilecek tek satirlik etiket."""
        parts = f"{self.artist_name} — {self.track_name}"
        if self.album_name:
            parts += f"  ·  {self.album_name}"
        if self.duration:
            m, s = divmod(int(self.duration), 60)
            parts += f"  ({m}:{s:02d})"
        return parts
