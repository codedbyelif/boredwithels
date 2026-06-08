"""BUILD-TIME: wordfreq ile TR/EN katmanli kelime listeleri uretir.

Calistir:  python scripts/generate_wordlists.py
Cikti:     src/kittytype/data/words/{tr,en}_{easy,medium,hard}.txt

Sadece harf iceren kelimeler alinir (noktalama/sayi yok). NFC normalize edilir.
Tier = frekans + uzunluk karisimi: easy=yaygin&kisa, medium=orta, hard=nadir&uzun.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

from wordfreq import top_n_list

OUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "kittytype"
    / "data"
    / "words"
)
LANGS = ("tr", "en")
PER_TIER = 320


def _clean(words):
    seen = set()
    out = []
    for w in words:
        w = unicodedata.normalize("NFC", w)
        if not w.isalpha():  # sadece harf: noktalama/sayi/kesme isareti vb. eler
            continue
        if w in seen:
            continue
        seen.add(w)
        out.append(w)
    return out


def build_tiers(lang: str):
    words = _clean(top_n_list(lang, 8000))
    easy = [w for w in words if len(w) <= 4][:PER_TIER]
    medium = [w for w in words if 5 <= len(w) <= 7][:PER_TIER]
    # hard: listenin daha derininden (daha nadir) ve uzun kelimeler
    hard = [w for w in words[1200:] if len(w) >= 7][:PER_TIER]
    return {"easy": easy, "medium": medium, "hard": hard}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        for tier, words in build_tiers(lang).items():
            path = OUT_DIR / f"{lang}_{tier}.txt"
            path.write_text("\n".join(words) + "\n", encoding="utf-8")
            print(f"{path.name}: {len(words)} kelime")


if __name__ == "__main__":
    main()
