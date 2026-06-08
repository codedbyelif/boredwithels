"""Siyah + pembe tema ve karakter karakter renklendirme stilleri."""
from __future__ import annotations

from rich.style import Style
from textual.theme import Theme

KITTYTYPE_THEME = Theme(
    name="kittytype",
    primary="#FF4FA3",      # sicak pembe - vurgular, basliklar, odak
    secondary="#FF8FC7",    # acik pembe - ikincil metin
    accent="#FF1E88",       # imlec / aktif vurgu
    foreground="#F5E6EF",   # beyaza yakin metin
    background="#0A0A0A",   # siyaha yakin arka plan
    surface="#141014",      # paneller / kartlar
    panel="#1E141B",        # daha derin panel
    success="#7CFFB2",
    warning="#FFD166",
    error="#FF5C7A",        # hatali karakter
    dark=True,
)

# TypingArea karakter stilleri (Rich Text ile satir ici uygulanir).
# config.engine.CharStatus.value anahtarlariyla eslesir: pending / correct / incorrect.
CHAR_STYLES = {
    "pending": Style(color="#6B5563"),                       # soluk gri - henuz yazilmadi
    "correct": Style(color="#F5E6EF"),                       # parlak - dogru
    "incorrect": Style(color="#0A0A0A", bgcolor="#FF5C7A"),  # siyah/pembe-bg - hatali
    "cursor": Style(color="#0A0A0A", bgcolor="#FF1E88", bold=True),  # imlec
}
