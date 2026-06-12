"""Kitaplik kayit/yukleme ve ilerleme testleri."""
from kitapkurdu.library import Library


def _add_sample(library: Library):
    return library.add(
        gutenberg_id=1342,
        title="Pride and Prejudice",
        author="Austen, Jane",
        language="en",
        text="Merhaba dünya.\nİkinci satır.",
    )


def test_add_and_reload(tmp_path):
    library = Library(data_dir=tmp_path)
    book = _add_sample(library)
    assert library.path_for(book).exists()

    reloaded = Library(data_dir=tmp_path)
    assert len(reloaded.books) == 1
    loaded = reloaded.books[0]
    assert loaded.title == "Pride and Prejudice"
    assert reloaded.read_text(loaded) == "Merhaba dünya.\nİkinci satır."


def test_add_is_idempotent(tmp_path):
    library = Library(data_dir=tmp_path)
    _add_sample(library)
    _add_sample(library)
    assert len(library.books) == 1


def test_progress_roundtrip_and_sort(tmp_path):
    library = Library(data_dir=tmp_path)
    first = _add_sample(library)
    second = library.add(gutenberg_id=2, title="İkinci", author="", language="tr", text="x")

    library.update_progress(first, 0.42)
    assert Library(data_dir=tmp_path).get(1342).progress == 0.42
    # update_progress sinirlari kirpar
    library.update_progress(second, 1.7)
    assert second.progress == 1.0
    # En son okunan en ustte
    assert library.sorted_books()[0] is second


def test_remove_deletes_file(tmp_path):
    library = Library(data_dir=tmp_path)
    book = _add_sample(library)
    path = library.path_for(book)
    library.remove(book)
    assert not path.exists()
    assert Library(data_dir=tmp_path).books == []


def test_settings_roundtrip(tmp_path):
    library = Library(data_dir=tmp_path)
    assert library.load_setting("theme") is None
    assert library.load_setting("theme", "kitapkurdu") == "kitapkurdu"
    library.save_setting("theme", "kitapkurdu-sepya")
    assert Library(data_dir=tmp_path).load_setting("theme") == "kitapkurdu-sepya"
    # bozuk ayar dosyasi sessizce yoksayilir
    library.settings_file.write_text("{bozuk", encoding="utf-8")
    assert library.load_setting("theme") is None


def test_missing_or_corrupt_json(tmp_path):
    assert Library(data_dir=tmp_path).books == []
    (tmp_path / "library.json").write_text("{bozuk", encoding="utf-8")
    assert Library(data_dir=tmp_path).books == []
