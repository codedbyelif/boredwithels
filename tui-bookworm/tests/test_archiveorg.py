"""Archive.org ayristirma ve OCR temizligi testleri (ag gerektirmez)."""
from bookworm.archiveorg.client import _parse_docs, clean_ocr
from bookworm.archiveorg.models import ArchiveBook


def test_parse_docs_handles_list_fields():
    docs = [
        {"identifier": "kitap-1", "title": "Safahat", "creator": ["Mehmet Âkif"], "downloads": 5},
        {"identifier": "kitap-2", "title": ["Çift", "Başlık"]},
        {"identifier": "", "title": "tanımlayıcısız"},  # elenir
        {"identifier": "bos-baslik"},  # elenir
    ]
    books = _parse_docs(docs)
    assert [b.identifier for b in books] == ["kitap-1", "kitap-2"]
    assert books[0].creator == "Mehmet Âkif"
    assert books[1].title == "Çift, Başlık"
    assert "5 indirme" in books[0].display
    assert "indirme" not in books[1].display


def test_clean_ocr():
    raw = "Os-  \nmanlı  tarihi  burada.\nDüz   satır.  "
    assert clean_ocr(raw) == "Osmanlı tarihi burada.\nDüz satır."


def test_book_id_stable_and_distinct():
    a = ArchiveBook(identifier="x", title="X")
    b = ArchiveBook(identifier="x", title="Başka başlık")
    c = ArchiveBook(identifier="y", title="X")
    assert a.book_id == b.book_id
    assert a.book_id != c.book_id
