"""Vikikaynak HTML ayristirma ve arama sonucu indirgeme testleri (ag gerektirmez)."""
from bookworm.wikisource.client import (
    _collapse_results,
    _natural_key,
    extract_author,
    html_to_text,
)
from bookworm.wikisource.models import WikisourceBook

SAMPLE_HTML = """<div class="mw-parser-output">
<div id="headerContainer" class="ws-noexport notheme noprint">
<b>Kürk Mantolu Madonna</b> <span class="fn">Sabahattin Ali</span>
</div>
<span style="display: none;">25097Gizli veri</span>
<p>Birinci paragraf.</p>
<span class="pagenum ws-pagenum" id="5"></span>
<p>İkinci paragraf,<br/>aynı paragrafta yeni satır.</p>
<style>.x { color: red }</style>
</div>"""


def test_html_to_text_skips_junk():
    text = html_to_text(SAMPLE_HTML)
    assert "Birinci paragraf." in text
    assert "İkinci paragraf,\naynı paragrafta yeni satır." in text
    # baslik sablonu, gizli veri, sayfa numarasi ve css metne girmez
    assert "Sabahattin Ali" not in text
    assert "Gizli veri" not in text
    assert "color: red" not in text


def test_extract_author():
    assert extract_author(SAMPLE_HTML) == "Sabahattin Ali"
    assert extract_author("<p>yazar yok</p>") == ""


def test_natural_key_sorts_chapters():
    titles = ["Kitap/Bölüm 10", "Kitap/Bölüm 2", "Kitap/Bölüm 1"]
    assert sorted(titles, key=_natural_key) == ["Kitap/Bölüm 1", "Kitap/Bölüm 2", "Kitap/Bölüm 10"]


def test_collapse_results_dedupes_subpages():
    items = [
        {"title": "Aşk-ı Memnu/Bölüm 2", "wordcount": 500},
        {"title": "Aşk-ı Memnu/Bölüm 1", "wordcount": 400},
        {"title": "Falaka", "wordcount": 1500},
    ]
    books = _collapse_results(items)
    assert [b.title for b in books] == ["Aşk-ı Memnu", "Falaka"]
    assert books[0].wordcount == 0  # alt sayfadan indirgendi, sayi bilinmiyor
    assert books[1].wordcount == 1500


def test_book_id_is_stable():
    a = WikisourceBook(title="Falaka")
    b = WikisourceBook(title="Falaka", wordcount=99)
    assert a.book_id == b.book_id
