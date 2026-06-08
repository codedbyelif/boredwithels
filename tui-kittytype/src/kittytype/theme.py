"""Temalar (siyah-pembe ve beyaz-pembe) + karakter karakter renklendirme stilleri."""
from __future__ import annotations

from rich.style import Style
from textual.color import Color
from textual.theme import Theme

# Siyah + pembe (varsayilan / koyu)
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

# Beyaz + pembe (acik)
KITTYTYPE_LIGHT_THEME = Theme(
    name="kittytype-light",
    primary="#D6206E",      # koyu pembe - beyaz uzerinde kontrast
    secondary="#B05C86",    # mat mor-pembe
    accent="#FF2D8E",       # sicak pembe imlec
    foreground="#3A1E2E",   # koyu erik metin
    background="#FFF5FA",   # beyaza yakin pembe ton
    surface="#FFE7F1",      # acik pembe panel
    panel="#FFD9EA",
    success="#2EA043",
    warning="#B26A00",
    error="#E5484D",        # hata icin kirmizi
    dark=False,
)


def char_styles(theme: Theme) -> dict:
    """Aktif temaya gore TypingArea karakter stilleri (Rich Text ile satir ici uygulanir).

    Renkler temadan turetildigi icin hem koyu hem acik temada okunakli kalir.
    """
    fg = theme.foreground or "#F5E6EF"
    bg = theme.background or "#0A0A0A"
    accent = theme.accent or theme.primary
    error = theme.error or "#FF5C7A"
    pending = Color.parse(fg).blend(Color.parse(bg), 0.55).hex  # soluk (henuz yazilmadi)
    return {
        "pending": Style(color=pending),
        "correct": Style(color=fg),
        "incorrect": Style(color=bg, bgcolor=error),
        "cursor": Style(color=bg, bgcolor=accent, bold=True),
    }
