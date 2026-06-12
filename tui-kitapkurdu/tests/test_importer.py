"""Yerel dosya ice aktarma testleri: TXT, EPUB ve PDF (ag gerektirmez)."""
import zipfile

import pytest

from kitapkurdu.importer import ImportFailed, book_id_for, import_file

# --- yardimcilar: testte gercek mini dosyalar uretilir ---


def _make_pdf(path, text="Merhaba PDF"):
    """Tek sayfalik, xref'i dogru hesaplanmis kucuk bir PDF yazar."""
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_at}\n%%EOF\n"
    ).encode()
    path.write_bytes(bytes(out))


_OPF = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
  <metadata><dc:title>Deneme Kitabı</dc:title><dc:creator>Elif</dc:creator></metadata>
  <manifest>
    <item id="c1" href="bolum1.xhtml" media-type="application/xhtml+xml"/>
    <item id="c2" href="bolum2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine><itemref idref="c1"/><itemref idref="c2"/></spine>
</package>"""

_CONTAINER = """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""


def _make_epub(path):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", _CONTAINER)
        zf.writestr("OEBPS/content.opf", _OPF)
        zf.writestr("OEBPS/bolum1.xhtml", "<html><body><p>Birinci bölüm metni.</p></body></html>")
        zf.writestr("OEBPS/bolum2.xhtml", "<html><body><p>İkinci bölüm metni.</p></body></html>")


# --- testler ---


def test_import_txt(tmp_path):
    f = tmp_path / "notlar.txt"
    f.write_text("Türkçe içerik: ğüşiöç", encoding="utf-8")
    title, author, text = import_file(f)
    assert title == "notlar"
    assert text == "Türkçe içerik: ğüşiöç"


def test_import_txt_cp1254_fallback(tmp_path):
    f = tmp_path / "eski.txt"
    f.write_bytes("Türkçe yazı".encode("cp1254"))
    _, _, text = import_file(f)
    assert text == "Türkçe yazı"


def test_import_pdf(tmp_path):
    f = tmp_path / "kitap.pdf"
    _make_pdf(f, text="Merhaba PDF")
    title, author, text = import_file(f)
    assert title == "kitap"  # metadata yoksa dosya adi
    assert "Merhaba PDF" in text


def test_import_epub(tmp_path):
    f = tmp_path / "kitap.epub"
    _make_epub(f)
    title, author, text = import_file(f)
    assert title == "Deneme Kitabı"
    assert author == "Elif"
    assert "Birinci bölüm metni." in text
    assert text.index("Birinci") < text.index("İkinci")  # spine sirasi korunur


def test_unsupported_and_empty(tmp_path):
    f = tmp_path / "resim.png"
    f.write_bytes(b"\x89PNG")
    with pytest.raises(ImportFailed):
        import_file(f)
    empty = tmp_path / "bos.txt"
    empty.write_text("   ", encoding="utf-8")
    with pytest.raises(ImportFailed):
        import_file(empty)


def test_book_id_stable(tmp_path):
    f = tmp_path / "kitap.pdf"
    assert book_id_for(f) == book_id_for(tmp_path / "kitap.pdf")
