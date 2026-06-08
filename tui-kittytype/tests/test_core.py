import unicodedata

from kittytype.core.engine import CharStatus, TypingEngine
from kittytype.core.stats import accuracy, gross_wpm, net_wpm
from kittytype.core.text_source import prepare_lyrics


def test_gross_wpm_basic():
    # 50 karakter, 60 sn -> 10 WPM
    assert round(gross_wpm(50, 60)) == 10


def test_zero_time_guard():
    assert gross_wpm(10, 0) == 0.0
    assert net_wpm(10, 2, 0) == 0.0


def test_accuracy():
    assert accuracy(0, 0) == 100.0
    assert accuracy(8, 10) == 80.0


def test_net_below_gross_with_errors():
    g = gross_wpm(100, 60)
    n = net_wpm(100, 5, 60)
    assert n < g


def test_engine_turkish_exact_match():
    target = "ışığı şöleni"
    eng = TypingEngine(target)
    for ch in target:
        eng.type_char(ch)
    assert eng.is_complete
    assert eng.incorrect_count == 0
    assert eng.correct_count == len(target)


def test_engine_incorrect_then_backspace():
    eng = TypingEngine("abc")
    eng.type_char("a")
    eng.type_char("x")  # yanlis
    assert eng.status_at(1) == CharStatus.INCORRECT
    assert eng.incorrect_count == 1
    eng.backspace()
    eng.type_char("b")
    assert eng.status_at(1) == CharStatus.CORRECT
    assert eng.total_keystrokes == 3   # a, x, b (backspace sayilmaz)
    assert eng.correct_keystrokes == 2  # a, b


def test_prepare_lyrics_keeps_lines_collapses_ws_nfc():
    raw = "Satır bir\n\nSatır iki\t  üç"
    out = prepare_lyrics(raw)
    # Satir yapisi korunur, bos satir atilir, satir ici bosluk daralir.
    assert out == "Satır bir\nSatır iki üç"
    assert "\t" not in out
    assert "  " not in out
    assert out == unicodedata.normalize("NFC", out)


def test_engine_space_or_enter_matches_newline():
    eng = TypingEngine("ab\ncd")
    for ch in "ab cd":  # satir sonunda newline yerine bosluk
        eng.type_char(ch)
    assert eng.is_complete
    assert eng.incorrect_count == 0
    assert eng.correct_count == 5
