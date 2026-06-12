# kitapkurdu

Terminal üzerinde çalışan, metin tabanlı (TUI) bir kitap okuyucudur.
Elif Kaynar tarafından Python ve Textual çatısı kullanılarak
geliştirilmiştir.

kitapkurdu is a terminal-based (TUI) book reader developed by Elif Kaynar
using Python and the Textual framework.

[Türkçe](#türkçe) · [English](#english)

---

## Türkçe

### Hakkında

kitapkurdu; Vikikaynak, Project Gutenberg ve Archive.org üzerinde arama
yapar, seçilen eseri indirir ve okuma ilerlemesini kalıcı olarak saklar.
Yerel diskteki PDF, EPUB ve düz metin dosyalarını da aynı okuyucu
arayüzünde açar. Tüm işlemler terminalden, uygulama dışına çıkmadan
gerçekleştirilir.

### Kitap kaynakları

| Kaynak | Açıklama |
| --- | --- |
| Vikikaynak | tr.wikisource.org üzerindeki telif süresi dolmuş Türkçe eserler. Bölümlere ayrılmış kitaplar doğal sırasıyla tek metinde birleştirilir; yazar bilgisi sayfadan otomatik alınır. |
| Project Gutenberg | 70.000'i aşkın ücretsiz kitap. Arama Gutendex API ile yapılır; hizmet yanıt vermediğinde Gutenberg'in resmî OPDS kataloğuna kendiliğinden geçilir. |
| Archive.org | Milyonlarca taranmış kitabın OCR metni. Tireyle bölünmüş kelimeler birleştirilir, fazla boşluklar temizlenir. |
| URL ile indirme | Arama kutusuna doğrudan bir PDF, EPUB veya TXT adresi yapıştırıldığında dosya indirilir, metni çıkarılır ve okuyucuda açılır. |
| Yerel dosya | Uygulama içindeki dosya gezgini ile diskteki PDF, EPUB, TXT ve MD dosyaları açılır. |

### Okuma özellikleri

- **Akış düzeni:** Kaynak metinlerdeki sabit satır kırılmaları
  (OCR ve PDF çıktılarında sık görülür) paragraf bütünlüğü korunarak
  ekran genişliğine göre yeniden düzenlenir. Şiir dizeleri, satır yapısı
  anlamlı olduğundan, olduğu gibi bırakılır; tek başına kalmış sayfa
  numaraları ayıklanır. `f` tuşu ile kaynaktaki özgün düzene dönülebilir.
- **İlerleme kaydı:** Her kitabın okunma konumu orana dayalı olarak
  saklanır; pencere boyutu veya sayfa düzeni değişse dahi okuma aynı
  noktadan sürer. Kitaplık ekranında ilerleme yüzde olarak görüntülenir.
- **Çevrimdışı kullanım:** İndirilen kitaplar yerel olarak saklanır;
  sonraki okumalar için ağ bağlantısı gerekmez.

### Temalar

`Ctrl+T` kısayolu dört tema arasında sırayla geçiş yapar; seçim kaydedilir
ve sonraki açılışta uygulanır.

| Tema | Açıklama |
| --- | --- |
| Koyu | Siyah zemin, pembe vurgular (varsayılan) |
| Açık | Beyaz zemin, pembe vurgular |
| Sepya | Krem zemin, kahverengi metin; gündüz okumaları için düşük kontrast |
| Gece | Koyu kahve zemin, kehribar metin; karanlık ortamda parlama yapmaz |

### Kurulum

Python 3.9 veya üzeri gerektirir.

```sh
cd tui-kitapkurdu
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kitapkurdu
```

### Kısayollar

| Tuş | İşlev |
| --- | --- |
| `s` | Kitap arama (Vikikaynak / Gutenberg / Archive.org) |
| `o` | Yerel dosya açma (PDF / EPUB / TXT / MD) |
| `Enter` | Kitabı açma veya indirme |
| `←` `→` `Boşluk` | Sayfa çevirme |
| `f` | Sayfa düzeni: akış / özgün |
| `Home` / `End` | Kitabın başına / sonuna gitme |
| `d` | Kitaplıktan silme |
| `Ctrl+T` | Tema değiştirme |
| `Esc` | Geri dönme |
| `q` | Çıkış |

### Veri konumu

Kitap metinleri, ilerleme bilgileri ve tema tercihi `~/.kitapkurdu/`
dizininde tutulur. Dizin silindiğinde tüm veriler kaybolur.

### Sınırlamalar

- Project Gutenberg kataloğunda Türkçe eser bulunmamaktadır; Türkçe
  içerik için kaynak Vikikaynak'tır. Gutenberg aramaları özgün
  (çoğunlukla İngilizce) başlık ve yazar adıyla en iyi sonucu verir.
- Yabancı eserlerin güncel Türkçe çevirileri, çevirmen telif hakları
  nedeniyle serbest kaynaklarda yer almaz; yalnızca Vikikaynak'taki
  telifsiz çeviriler erişilebilir durumdadır.
- Archive.org metinleri OCR ürünüdür; özellikle eski baskılarda karakter
  hataları görülebilir.
- Yalnızca görüntüden oluşan (taranmış) PDF dosyalarında çıkarılabilir
  metin bulunmadığından bu dosyalar açılamaz.

### Geliştirme

```sh
pip install -e ".[dev]"
pytest          # birim testleri
ruff check .    # statik denetim
```

---

## English

### About

kitapkurdu searches Wikisource, Project Gutenberg and Archive.org,
downloads the selected work and stores reading progress persistently.
It also opens local PDF, EPUB and plain-text files in the same reader
interface. All operations take place in the terminal, without leaving
the application.

### Book sources

| Source | Description |
| --- | --- |
| Wikisource | Public-domain Turkish works on tr.wikisource.org. Works split into chapters are stitched into a single text in natural order; author information is extracted automatically. |
| Project Gutenberg | More than 70,000 free books. Search is performed through the Gutendex API, falling back to Gutenberg's official OPDS catalogue automatically when the service is unresponsive. |
| Archive.org | OCR text of millions of scanned books. Hyphenated line breaks are joined and excess whitespace is removed. |
| Download by URL | Pasting a direct PDF, EPUB or TXT address into the search box downloads the file, extracts its text and opens it in the reader. |
| Local files | PDF, EPUB, TXT and MD files on disk are opened through the built-in file browser. |

### Reading features

- **Flow layout:** Fixed line breaks present in source texts (common in
  OCR and PDF output) are reflowed to the terminal width while paragraph
  integrity is preserved. Verse lines are kept intact, since their line
  structure is meaningful, and stray page numbers are removed. The `f`
  key switches back to the original layout.
- **Progress tracking:** The reading position of each book is stored as
  a ratio, so reading resumes from the same point even if the window
  size or layout changes. Progress is shown as a percentage on the
  shelf screen.
- **Offline use:** Downloaded books are stored locally; no network
  connection is required for subsequent reading.

### Themes

The `Ctrl+T` shortcut cycles through four themes; the selection is saved
and restored on the next launch.

| Theme | Description |
| --- | --- |
| Dark | Black background with pink accents (default) |
| Light | White background with pink accents |
| Sepia | Cream background with brown text; low contrast for daytime reading |
| Night | Dark brown background with amber text; glare-free in dark environments |

### Installation

Requires Python 3.9 or later.

```sh
cd tui-kitapkurdu
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kitapkurdu
```

### Key bindings

| Key | Function |
| --- | --- |
| `s` | Search for books (Wikisource / Gutenberg / Archive.org) |
| `o` | Open a local file (PDF / EPUB / TXT / MD) |
| `Enter` | Open or download the selected book |
| `←` `→` `Space` | Turn pages |
| `f` | Layout: flow / original |
| `Home` / `End` | Jump to the beginning / end |
| `d` | Remove from the shelf |
| `Ctrl+T` | Cycle themes |
| `Esc` | Go back |
| `q` | Quit |

### Data location

Book texts, progress records and the theme preference are kept under
`~/.kitapkurdu/`. Deleting this directory removes all data.

### Limitations

- The Project Gutenberg catalogue contains no Turkish works; Wikisource
  is the source for Turkish content. Gutenberg searches yield the best
  results with original (mostly English) titles and author names.
- Recent Turkish translations of foreign works are not available in free
  sources due to translator copyright; only public-domain translations
  on Wikisource are accessible.
- Archive.org texts are OCR output; character errors may occur,
  particularly in older editions.
- Image-only (scanned) PDF files cannot be opened, as they contain no
  extractable text.

### Development

```sh
pip install -e ".[dev]"
pytest          # unit tests
ruff check .    # static analysis
```

---

## Lisans / License

Bu proje MIT lisansı ile lisanslanmıştır; ayrıntılar için [LICENSE](LICENSE)
dosyasına bakınız. / This project is licensed under the MIT License; see
the [LICENSE](LICENSE) file for details.

Telif Hakkı (c) 2026 Elif Kaynar — tasarım ve geliştirme Elif Kaynar'a
aittir. / Copyright (c) 2026 Elif Kaynar — designed and developed by
Elif Kaynar.
