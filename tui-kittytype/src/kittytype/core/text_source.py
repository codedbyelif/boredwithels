"""Yazilacak metni uretir: rastgele kelime akisi ve sarki sozu hazirligi."""
from __future__ import annotations

import random
import re
import unicodedata
from pathlib import Path
from typing import List

from kittytype.config import RANDOM_WORD_COUNT, Difficulty, Language

# data/words klasoru bu dosyaya gore: core/ -> kittytype/ -> data/words/
_WORDS_DIR = Path(__file__).resolve().parent.parent / "data" / "words"
_MAX_LYRICS_CHARS = 3000


def _load_words(language: Language, difficulty: Difficulty) -> List[str]:
    path = _WORDS_DIR / f"{language.value}_{difficulty.value}.txt"
    text = path.read_text(encoding="utf-8")
    return [w for w in text.split() if w]


def build_random_text(
    language: Language,
    difficulty: Difficulty,
    word_count: int = RANDOM_WORD_COUNT,
) -> str:
    """Secilen dil/zorluk havuzundan rastgele kelimeleri boslukla birlestirir."""
    pool = _load_words(language, difficulty)
    if not pool:
        return ""
    words = random.choices(pool, k=word_count)
    return " ".join(words)


def prepare_lyrics(raw: str) -> str:
    """Sarki sozunu yazilabilir hale getir, SATIR YAPISINI KORUYARAK.

    - NFC normalize (ör. 'o' tek kod noktasi olsun).
    - Her satir icindeki coklu bosluk/sekme tek bosluga iner.
    - Bos satirlar atilir (dizeler alt alta, bos satir olmadan).
    - Satirlar '\\n' ile korunur; yazarken satir sonu Space (veya Enter) ile gecilir.
    """
    text = unicodedata.normalize("NFC", raw)
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t \r\f\v]+", " ", line).strip()
        if line:
            lines.append(line)
    text = "\n".join(lines)
    if len(text) > _MAX_LYRICS_CHARS:
        text = text[:_MAX_LYRICS_CHARS]
        nl = text.rfind("\n")  # son tam satira kadar kirp
        text = (text[:nl] if nl > 0 else text).rstrip()
    return text
