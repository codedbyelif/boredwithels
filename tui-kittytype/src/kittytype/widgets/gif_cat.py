"""Gercek GIF'i terminalde oynatan widget.

Her kare renkli yarim-blok karakterlerine cevrilir (ust yarim '▀', alt yarim '▄'):
bir karakter hucresi = 2 dikey piksel. Saydam pikseller renksiz birakilir, boylece
widget'in (aktif temanin) arka planini gosterir; GIF her temada dogru gorunur.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from rich.style import Style
from rich.text import Text
from textual.widgets import Static

_GIF_PATH = Path(__file__).resolve().parent.parent / "data" / "hello-kitty.gif"
_UPPER = "▀"
_LOWER = "▄"
_ALPHA = 128  # bu degerin altindaki piksel saydam sayilir -> widget arka plani

_cache: Dict[int, Tuple[List[Text], List[float]]] = {}


def _hx(p) -> str:
    return f"#{p[0]:02x}{p[1]:02x}{p[2]:02x}"


def _frame_to_text(img, cols: int, rows: int) -> Text:
    px = img.load()
    h = rows * 2
    text = Text(no_wrap=True, end="")
    for ry in range(rows):
        ty = ry * 2
        for cx in range(cols):
            top = px[cx, ty]
            bot = px[cx, ty + 1] if ty + 1 < h else (0, 0, 0, 0)
            top_op = top[3] >= _ALPHA
            bot_op = bot[3] >= _ALPHA
            if top_op and bot_op:
                text.append(_UPPER, style=Style(color=_hx(top), bgcolor=_hx(bot)))
            elif top_op:
                text.append(_UPPER, style=Style(color=_hx(top)))   # alt yari = widget bg
            elif bot_op:
                text.append(_LOWER, style=Style(color=_hx(bot)))   # ust yari = widget bg
            else:
                text.append(" ")                                    # tamamen saydam
        if ry != rows - 1:
            text.append("\n")
    return text


def load_frames(cols: int) -> Tuple[List[Text], List[float]]:
    """GIF karelerini Rich Text listesine + saniye cinsinden kare surelerine cevirir.

    Pillow yoksa ImportError firlatir (cagiran taraf ASCII'ye duser).
    """
    if cols in _cache:
        return _cache[cols]

    from PIL import Image, ImageSequence  # gecikmeli import

    im = Image.open(_GIF_PATH)
    w, h = im.size
    rows = max(1, round(cols * h / (w * 2)))  # yarim-blok: rows = cols*(h/w)/2
    px_h = rows * 2

    frames: List[Text] = []
    intervals: List[float] = []
    for frame in ImageSequence.Iterator(im):
        rgba = frame.convert("RGBA").resize((cols, px_h), Image.LANCZOS)
        frames.append(_frame_to_text(rgba, cols, rows))
        dur = frame.info.get("duration", 100) or 100
        intervals.append(min(0.12, max(0.05, dur / 1000.0)))  # canli ama makul hiz

    _cache[cols] = (frames, intervals)
    return _cache[cols]


class GifCat(Static):
    """Yuklenen kareleri kendi surelerine gore donduren animasyonlu widget."""

    def __init__(self, frames: List[Text], intervals: List[float], **kwargs) -> None:
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
