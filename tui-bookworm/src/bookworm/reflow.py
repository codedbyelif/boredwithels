"""Okuma metnini ekrana hazirlama: akis duzeni (reflow) ve sayfalama satirlari.

Kaynak metinler (Gutenberg, OCR, PDF) sabit genislige gore kirilmis gelir;
dar/genis ekranda bu kirilmalar okumayi bozar. Akis duzeni paragraflari
birlestirip ekran genisligine gore yeniden katlar. Siir gibi satir yapisi
anlamli bloklar (dizeler kisa ve birbirine yakin uzunluktadir) oldugu gibi
korunur. Orijinal duzen istenirse flow=False ile eski satir yapisi kalir.
"""
from __future__ import annotations

import re
import textwrap
from typing import List

_PAGE_NUMBER_RE = re.compile(r"^\d{1,4}$")  # OCR'da tek basina kalan sayfa numaralari
# Bir paragrafin son satiri: cumle bitiren isaretle biter ve satir belirgin kisadir
_PARA_END_CHARS = (".", "!", "?", "…", ":", ";", "»", "”", '"', "'", ")")
_VERSE_MAX_LEN = 55     # dize sayilacak satirlarin tipik ust siniri
_SHORT_LINE_RATIO = 0.75


def _split_blocks(text: str) -> List[List[str]]:
    """Bos satirlarla ayrilmis bloklar; sayfa numarasi satirlari atilir."""
    blocks: List[List[str]] = []
    current: List[str] = []
    for raw in text.splitlines():
        line = raw.replace("\x0c", " ").strip()
        if _PAGE_NUMBER_RE.match(line):
            continue
        if not line:
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _is_verse(block: List[str]) -> bool:
    """Dize blogu: en az iki satir ve satirlarin ezici cogunlugu kisa."""
    if len(block) < 2:
        return False
    lengths = sorted(len(line) for line in block)
    p90 = lengths[int(0.9 * (len(lengths) - 1))]
    return p90 <= _VERSE_MAX_LEN


def _paragraphs(block: List[str]) -> List[str]:
    """Sert kirilmis satirlari paragraflara birlestirir.

    PDF metinlerinde paragraflar arasinda bos satir olmayabilir; 'kisa ve
    noktalamayla biten satir' paragraf sonu sayilarak bunlar da ayristirilir.
    """
    max_len = max(len(line) for line in block)
    paragraphs: List[str] = []
    current: List[str] = []
    for line in block:
        current.append(line)
        if line.endswith(_PARA_END_CHARS) and len(line) < max_len * _SHORT_LINE_RATIO:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def build_lines(text: str, width: int, flow: bool = True) -> List[str]:
    """Metni verilen genislikte goruntuleme satirlarina cevirir."""
    width = max(20, width)
    out: List[str] = []
    if not flow:
        # Orijinal duzen: satir yapisi korunur, sadece tasan satirlar katlanir
        for raw in text.splitlines():
            raw = raw.rstrip()
            if not raw:
                out.append("")
            else:
                out.extend(textwrap.wrap(raw, width=width) or [""])
        return out or [""]

    for block in _split_blocks(text):
        if _is_verse(block):
            for line in block:
                out.extend(textwrap.wrap(line, width=width, subsequent_indent="    ") or [""])
        else:
            for i, para in enumerate(_paragraphs(block)):
                if i:
                    out.append("")
                out.extend(textwrap.wrap(para, width=width) or [""])
        out.append("")
    while out and not out[-1]:
        out.pop()
    return out or [""]
