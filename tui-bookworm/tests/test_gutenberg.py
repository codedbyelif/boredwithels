"""Gutendex/OPDS ayristirma ve lisans kalibi ayiklama testleri (ag gerektirmez)."""
from bookworm.gutenberg.client import _parse_book, _parse_opds, _plain_text_url, strip_boilerplate

SAMPLE_ITEM = {
    "id": 1342,
    "title": "Pride and Prejudice",
    "authors": [{"name": "Austen, Jane", "birth_year": 1775, "death_year": 1817}],
    "languages": ["en"],
    "download_count": 12345,
    "formats": {
        "application/epub+zip": "https://www.gutenberg.org/ebooks/1342.epub3.images",
        "text/plain; charset=us-ascii": "https://www.gutenberg.org/files/1342/1342-0.txt",
    },
}


def test_parse_book():
    book = _parse_book(SAMPLE_ITEM)
    assert book.id == 1342
    assert book.author == "Austen, Jane"
    assert book.language == "en"
    assert book.text_url == "https://www.gutenberg.org/files/1342/1342-0.txt"
    assert "12,345" in book.display


def test_plain_text_url_skips_zip():
    formats = {
        "text/plain; charset=utf-8": "https://example.org/x.txt.zip",
        "application/epub+zip": "https://example.org/x.epub",
    }
    assert _plain_text_url(formats) is None
    formats["text/plain"] = "https://example.org/x.txt"
    assert _plain_text_url(formats) == "https://example.org/x.txt"


OPDS_SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<id>http://www.gutenberg.org/ebooks/search.opds/?query=pride</id>
<title>Books: pride</title>
<entry>
<id>https://www.gutenberg.org/ebooks/1342.opds</id>
<title>Pride and Prejudice</title>
<content type="text">Jane Austen</content>
</entry>
<entry>
<id>https://www.gutenberg.org/ebooks/search.opds/?query=bos</id>
<title>No records found.</title>
</entry>
</feed>
"""


def test_parse_opds():
    books = _parse_opds(OPDS_SAMPLE, "en")
    assert len(books) == 1
    book = books[0]
    assert book.id == 1342
    assert book.title == "Pride and Prejudice"
    assert book.author == "Jane Austen"
    assert book.text_url is None
    assert "indirme" not in book.display  # sayi bilinmiyorsa gosterilmez


def test_parse_opds_invalid_xml():
    assert _parse_opds("bu xml degil", "") == []


def test_strip_boilerplate():
    text = (
        "The Project Gutenberg eBook of X\n"
        "lisans laflari...\n"
        "*** START OF THE PROJECT GUTENBERG EBOOK X ***\n"
        "Birinci bölüm.\n"
        "\n"
        "Hikâye burada.\n"
        "*** END OF THE PROJECT GUTENBERG EBOOK X ***\n"
        "daha fazla lisans...\n"
    )
    assert strip_boilerplate(text) == "Birinci bölüm.\n\nHikâye burada."


def test_strip_boilerplate_without_markers():
    text = "Sadece metin.\nİkinci satır."
    assert strip_boilerplate(text) == text
