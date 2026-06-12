"""Akis duzeni (reflow) testleri."""
from kitapkurdu.reflow import build_lines

# ~60 sutuna sert kirilmis tipik Gutenberg/OCR paragrafi
PROSE = (
    "Her sabah erkenden kalkar, bahcedeki kus seslerini dinleyerek\n"
    "uzun uzun kahvalti ederdik; sonra sahile inip balikcilarin\n"
    "donmesini beklerdik.\n"
    "\n"
    "Ertesi gun yagmur yagdi.\n"
)

VERSE = (
    "Korkma! Sonmez bu safaklarda yuzen al sancak,\n"
    "Sonmeden yurdumun ustunde tuten en son ocak.\n"
    "O benim milletimin yildizidir, parlayacak;\n"
    "O benimdir, o benim milletimindir ancak.\n"
)

# PDF cikarimi: paragraflar arasinda bos satir yok, son satirlar kisa + noktali
PDF_LIKE = (
    "Bu uzun bir cumledir ve sayfanin genisligine kadar devam eder durur\n"
    "ama burada biter.\n"
    "Yeni paragraf da ayni sekilde uzun uzun devam eden bir cumleyle\n"
    "baslar ve kisa biter.\n"
)


def test_prose_is_reflowed_to_width():
    lines = build_lines(PROSE, width=40)
    assert all(len(line) <= 40 for line in lines)
    # iki ayri paragraf, arada bos satir
    text = "\n".join(lines)
    assert "dinleyerek uzun" in text.replace("\n", " ") or "dinleyerek\nuzun" in text
    assert "\n\nErtesi gun" in text


def test_verse_lines_are_preserved():
    lines = [line for line in build_lines(VERSE, width=70) if line]
    assert lines[0] == "Korkma! Sonmez bu safaklarda yuzen al sancak,"
    assert len(lines) == 4  # dort dize, birlesmemis


def test_pdf_paragraph_split_on_short_punctuated_line():
    lines = build_lines(PDF_LIKE, width=70)
    text = "\n".join(lines)
    assert "ama burada biter.\n\nYeni paragraf" in text


def test_page_numbers_dropped_in_flow():
    text = "Paragraf metni burada.\n\n42\n\nDevami burada."
    flat = "\n".join(build_lines(text, width=70))
    assert "42" not in flat


def test_flow_off_preserves_structure():
    lines = build_lines(PROSE, width=200, flow=False)
    assert lines[0] == "Her sabah erkenden kalkar, bahcedeki kus seslerini dinleyerek"
    assert "" in lines  # bos satirlar duruyor


def test_long_verse_line_wraps_with_indent():
    verse = "kisa dize bir,\nkisa dize iki,\n" + ("cok " * 30) + "uzun dize.\n" + "kisa dize uc,\n"
    lines = build_lines(verse, width=40)
    wrapped = [line for line in lines if line.startswith("    ")]
    assert wrapped, "tasan dize girintiyle katlanmali"


def test_empty_text():
    assert build_lines("", width=40) == [""]
    assert build_lines("", width=40, flow=False) == [""]
