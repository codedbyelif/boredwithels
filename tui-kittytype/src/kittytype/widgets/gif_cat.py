"""Gercek GIF'i terminalde oynatan widget.

Her GIF karesi renkli yarim-blok (U+2580 '▀') karakterlerine cevrilir: bir karakter
hucresi ust pikseli on-plan, alt pikseli arka-plan rengiyle gosterir -> 2 dikey piksel.
Bu sayede her terminalde (sixel/protokol gerekmeden) renkli, animasyonlu gorunur.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from rich.style import Style
from rich.text import Text
from textual.widgets import Static

_GIF_PATH = Path(__file__).resolve().parent.parent / "data" / "hello-kitty.gif"
_HALF = "▀"

# (cols, bg) -> (frames, intervals) onbellegi (bir kez yukle)
_cache: Dict[Tuple[int, Tuple[int, int, int]], Tuple[List[Text], List[float]]] = {}


def _hexrgb(p) -> str:
    return f"#{p[0]:02x}{p[1]:02x}{p[2]:02x}"


def _frame_to_text(img, cols: int, rows: int) -> Text:
    px = img.load()
    h = rows * 2
    text = Text(no_wrap=True, end="")
    for ry in range(rows):
        ty = ry * 2
        for cx in range(cols):
            top = px[cx, ty]
            bot = px[cx, ty + 1] if ty + 1 < h else top
            text.append(_HALF, style=Style(color=_hexrgb(top), bgcolor=_hexrgb(bot)))
        if ry != rows - 1:
            text.append("\n")
    return text


def load_frames(
    cols: int, bg_rgb: Tuple[int, int, int]
) -> Tuple[List[Text], List[float]]:
    """GIF karelerini Rich Text listesine + saniye cinsinden kare surelerine cevirir.

    Saydam pikseller `bg_rgb` (panel arka plani) ile harmanlanir, boylece kutuya kaynar.
    Pillow yoksa ImportError firlatir (cagiran taraf ASCII'ye duser).
    """
    key = (cols, bg_rgb)
    if key in _cache:
        return _cache[key]

    from PIL import Image, ImageSequence  # gecikmeli import: Pillow yoksa fallback

    im = Image.open(_GIF_PATH)
    w, h = im.size
    # Yarim-blok: 1 karakter = 1px genis x 2px yuksek. Terminal hucresi ~2x uzun
    # oldugundan en-boy korunur: rows = cols * (h/w) / 2.
    rows = max(1, round(cols * h / (w * 2)))
    px_h = rows * 2
    bg = Image.new("RGBA", (w, h), bg_rgb + (255,))

    frames: List[Text] = []
    intervals: List[float] = []
    for frame in ImageSequence.Iterator(im):
        rgba = frame.convert("RGBA")
        composed = Image.alpha_composite(bg, rgba).convert("RGB")
        small = composed.resize((cols, px_h), Image.LANCZOS)
        frames.append(_frame_to_text(small, cols, rows))
        dur = frame.info.get("duration", 100) or 100
        intervals.append(min(0.12, max(0.05, dur / 1000.0)))  # canli ama makul hiz

    result = (frames, intervals)
    _cache[key] = result
    return result


class GifCat(Static):
    """Yuklenen kareleri kendi surelerine gore donduren animasyonlu widget."""

    def __init__(
        self, frames: List[Text], intervals: List[float], **kwargs
    ) -> None:
        super().__init__(frames[0], **kwargs)
        self._frames = frames
        self._intervals = intervals
        self._i = 0
        self._timer = None

    def on_mount(self) -> None:
        self._schedule()

    def _schedule(self) -> None:
        self._timer = self.set_timer(self._intervals[self._i], self._advance)

    def _advance(self) -> None:
        self._i = (self._i + 1) % len(self._frames)
        self.update(self._frames[self._i])
        self._schedule()

    def on_unmount(self) -> None:
        if self._timer is not None:
            self._timer.stop()
