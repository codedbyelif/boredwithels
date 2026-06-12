"""Temalar: kittytype paleti (koyu/acik pembe) + goz yormayan sepya okuma temasi."""
from __future__ import annotations

from textual.theme import Theme

# Siyah + pembe (varsayilan / koyu)
BOOKWORM_THEME = Theme(
    name="bookworm",
    primary="#FF4FA3",      # sicak pembe - vurgular, basliklar, odak
    secondary="#FF8FC7",    # acik pembe - ikincil metin
    accent="#FF1E88",       # aktif vurgu
    foreground="#F5E6EF",   # beyaza yakin metin
    background="#0A0A0A",   # siyaha yakin arka plan
    surface="#141014",      # paneller / kartlar
    panel="#1E141B",        # daha derin panel
    success="#7CFFB2",
    warning="#FFD166",
    error="#FF5C7A",
    dark=True,
)

# Gece (goz yormayan koyu tema): simsiyah yerine sicak koyu kahve zemin,
# bembeyaz yerine krem-kehribar metin. Karanlik ortamda parlama yapmaz.
BOOKWORM_NIGHT_THEME = Theme(
    name="bookworm-night",
    primary="#D9A05B",      # kehribar - basliklar, vurgular
    secondary="#A98F6C",    # mat kum - ikincil metin
    accent="#E3B341",       # sicak sari vurgu
    foreground="#E8D5B0",   # krem-kehribar metin (hafif sari, beyaz degil)
    background="#262019",   # sicak koyu kahve zemin (siyah degil)
    surface="#2E2720",      # paneller
    panel="#382F25",
    success="#7FA56B",
    warning="#D79921",
    error="#C26D5C",
    dark=True,
)

# Sepya (goz yormayan okuma temasi): krem zemin + koyu kahve metin,
# e-murekkep okuyucularin klasik duzeni. Kontrast dusuk, sicak tonlar.
BOOKWORM_SEPIA_THEME = Theme(
    name="bookworm-sepia",
    primary="#9C5B45",      # sicak kiremit - basliklar, vurgular
    secondary="#8A715A",    # mat kahve - ikincil metin
    accent="#B5654A",       # aktif vurgu
    foreground="#5B4636",   # koyu kahve metin (siyah degil, yumusak)
    background="#F4ECD8",   # krem / sepya zemin
    surface="#EFE4CC",      # paneller
    panel="#E8DABB",
    success="#5C7C50",
    warning="#9A6B00",
    error="#A9504A",
    dark=False,
)

# Beyaz + pembe (acik)
BOOKWORM_LIGHT_THEME = Theme(
    name="bookworm-light",
    primary="#D6206E",      # koyu pembe - beyaz uzerinde kontrast
    secondary="#B05C86",    # mat mor-pembe
    accent="#FF2D8E",       # sicak pembe vurgu
    foreground="#3A1E2E",   # koyu erik metin
    background="#FFF5FA",   # beyaza yakin pembe ton
    surface="#FFE7F1",      # acik pembe panel
    panel="#FFD9EA",
    success="#2EA043",
    warning="#B26A00",
    error="#E5484D",
    dark=False,
)
