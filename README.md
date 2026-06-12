# boredwithels

Öncelikle, repoma göz attığınız için teşekkür ederim. Burada hem kitty
terminalinde hem de VS Code'un  terminalinde eğlenebileceğiniz
aktiviteler mevcut. Keyifle kullanmanız dileğiyle; herhangi bir sorunla
karşılaşırsanız issue açmaktan çekinmeyin, seviliyorsunuz!!

First of all, thank you for taking a look at my repository. It offers
activities you can enjoy both in the kitty terminal and in the integrated
VS Code terminal. I hope you have fun with it; if you run into any
problems, do not hesitate to open an issue — you are loved!!

Bu depo, Elif Kaynar tarafından geliştirilen ve terminal üzerinde çalışan
uygulamaların toplandığı depodur. Her proje kendi dizininde bağımsız
olarak yer alır; kendi kurulum yönergelerini, testlerini ve lisans
dosyasını içerir.

This repository is a collection of terminal applications developed by
Elif Kaynar. Each project resides independently in its own directory and
includes its own installation instructions, tests and license file.

[Türkçe](#türkçe) · [English](#english)

---

## Türkçe

### Hakkında

Depodaki projelerin ortak noktası, grafik arayüz veya tarayıcı
gerektirmeden tüm işlevlerini terminal içinde sunmalarıdır. İki proje
Python ve Textual çatısıyla yazılmış tam ekran metin arayüzleri (TUI),
biri ise kabuk betiklerinden oluşan bir araç takımıdır.

### Depo yapısı

```
boredwithels/
├── tui-kitapkurdu/    Terminal kitap okuyucu (Python, Textual)
├── tui-kittytype/     Terminal yazma hızı testi (Python, Textual)
└── youtube-terminal/  Terminalde YouTube oynatıcı ve birlikte izleme (Shell)
```

### tui-kitapkurdu — terminal kitap okuyucu

Çevrim içi kaynaklarda kitap arayan, indiren ve terminalde sayfa sayfa
okutan bir uygulamadır. Ayrıntılar için [tui-kitapkurdu/README.md](tui-kitapkurdu/README.md)
dosyasına bakınız.

Öne çıkan özellikler:

- Üç çevrim içi kaynakta arama: Vikikaynak (telifsiz Türkçe eserler),
  Project Gutenberg (70.000'i aşkın kitap; Gutendex API, yanıt
  alınamadığında resmî OPDS kataloğuna otomatik geçiş) ve Archive.org
  (taranmış kitapların OCR metinleri).
- URL ile indirme: arama kutusuna yapıştırılan doğrudan PDF/EPUB/TXT
  adresi indirilip okuyucuda açılır.
- Yerel dosya desteği: uygulama içindeki dosya gezgini ile diskteki
  PDF, EPUB, TXT ve MD dosyaları açılır.
- Akış düzeni: OCR ve PDF metinlerindeki sabit satır kırılmaları
  paragraf bütünlüğü korunarak ekran genişliğine göre yeniden
  düzenlenir; şiir dizeleri korunur, sayfa numarası artıkları ayıklanır.
- Okuma ilerlemesi orana dayalı saklanır; pencere boyutu değişse bile
  kaldığı noktadan sürer ve kitaplıkta yüzde olarak görüntülenir.
- Dört tema (koyu, açık, sepya, gece); seçim kaydedilir. Sepya ve gece
  temaları uzun okumalarda göz yorgunluğunu azaltacak biçimde
  düzenlenmiştir.

Gereksinimler: Python 3.9+, ağ bağlantısı (yalnızca arama ve indirme
için). Hızlı başlangıç:

```sh
cd tui-kitapkurdu
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kitapkurdu
```

### tui-kittytype — terminal yazma hızı testi

Siyah-pembe temalı bir yazma hızı (WPM) testidir. Ayrıntılar için
[tui-kittytype/README.md](tui-kittytype/README.md) dosyasına bakınız.

Öne çıkan özellikler:

- Rastgele kelime modu: 15 / 30 / 60 / 120 saniyelik süre seçenekleri,
  anlık WPM ve isabet yüzdesi.
- Şarkı sözü modu: LRCLIB servisi üzerinden (API anahtarı gerekmez)
  şarkı aranır ve gerçek sözler satır satır yazılır.
- Üç zorluk seviyesi (kolay / orta / zor) ve Türkçe ile İngilizce kelime
  havuzları; Türkçe karakterler (ı ğ ş ç ö ü) büyük-küçük harf duyarlı
  olarak doğrulanır.
- Karakter bazında renklendirme (doğru / yanlış / imleç / bekleyen) ve
  sonuç ekranında net WPM, brüt WPM, isabet ve süre bilgileri.
- Ana menüde herhangi bir terminalde çalışan animasyonlu Hello Kitty
  görseli; koyu ve açık pembe temalar arasında geçiş.

Gereksinimler: Python 3.9+, en az 80x24 boyutunda bir terminal; ağ
bağlantısı yalnızca şarkı sözü modu için gerekir. Hızlı başlangıç:

```sh
cd tui-kittytype
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kittytype
```

### youtube-terminal — terminalde YouTube

YouTube videolarını tarayıcı veya grafik arayüz olmadan, doğrudan
terminal içinde (VS Code tümleşik terminali dahil) oynatan ve ortak
izleme oturumları kuran kabuk betikleridir. macOS hedeflenmiştir.
Ayrıntılar için [youtube-terminal/README.md](youtube-terminal/README.md)
dosyasına bakınız.

İçerdiği araçlar:

- `yt-vscode`: Videoyu VS Code terminalinde oynatır. Ses ve zamanlama
  `mpv` ile, görüntü `ffmpeg` kareleri üzerinden `chafa` tarafından
  renkli karakter blokları olarak çizilir; ileri-geri sarmada ses ve
  görüntü yeniden eşitlenir.
- `watch-together`: `tmate` aracılığıyla internet üzerinden ortak izleme
  bağlantısı üretir; karşı tarafın kurulum yapması gerekmez.
- `watch-together-lan`: Aynı ağdaki bir kişinin SSH ile katıldığı
  `tmux` oturumu açar; internet bağlantısı gerektirmez.
- `ytfzf-kitty-ayar.sh` ve `ytfzf-vscode-ayar.sh`: kitty ve VS Code
  terminalleri için hazır `ytfzf` yapılandırmaları.

Gereksinimler ve kurulum:

```sh
brew install yt-dlp mpv ffmpeg chafa ytfzf
brew install tmate tmux      # birlikte izleme için
```

### Geliştirme

Python projelerinde testler ve statik denetim şu şekilde çalıştırılır:

```sh
pip install -e ".[dev]"
pytest          # birim testleri
ruff check .    # statik denetim
```

### Lisans

Depo genelinde MIT lisansı geçerlidir; bkz. [LICENSE](LICENSE). Alt
projelerin kendi dizinlerindeki lisans dosyaları da aynı koşulları taşır.

---

## English

### About

The common trait of the projects in this repository is that they deliver
all of their functionality inside the terminal, without requiring a
graphical interface or a browser. Two projects are full-screen text user
interfaces (TUI) written in Python with the Textual framework; the third
is a toolset composed of shell scripts.

### Repository structure

```
boredwithels/
├── tui-kitapkurdu/    Terminal book reader (Python, Textual)
├── tui-kittytype/     Terminal typing-speed test (Python, Textual)
└── youtube-terminal/  YouTube player and watch-together in the terminal (Shell)
```

### tui-kitapkurdu — terminal book reader

An application that searches online sources, downloads books and presents
them page by page in the terminal. See
[tui-kitapkurdu/README.md](tui-kitapkurdu/README.md) for details.

Highlights:

- Search across three online sources: Wikisource (public-domain Turkish
  works), Project Gutenberg (over 70,000 books; Gutendex API with an
  automatic fallback to the official OPDS catalogue) and Archive.org
  (OCR text of scanned books).
- Download by URL: a direct PDF/EPUB/TXT address pasted into the search
  box is downloaded and opened in the reader.
- Local file support: PDF, EPUB, TXT and MD files on disk are opened
  through the built-in file browser.
- Flow layout: fixed line breaks in OCR and PDF texts are reflowed to
  the terminal width while paragraph integrity is preserved; verse lines
  are kept intact and stray page numbers are removed.
- Reading progress is stored as a ratio; reading resumes from the same
  point even if the window size changes, and progress is shown as a
  percentage on the shelf.
- Four themes (dark, light, sepia, night) with a persisted selection.
  The sepia and night themes are tuned to reduce eye strain during long
  reading sessions.

Requirements: Python 3.9+; a network connection is needed only for
searching and downloading. Quick start:

```sh
cd tui-kitapkurdu
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kitapkurdu
```

### tui-kittytype — terminal typing-speed test

A black-and-pink typing-speed (WPM) test. See
[tui-kittytype/README.md](tui-kittytype/README.md) for details.

Highlights:

- Random-words mode: timed tests of 15 / 30 / 60 / 120 seconds with live
  WPM and accuracy.
- Song-lyrics mode: songs are searched through the LRCLIB service (no
  API key required) and the actual lyrics are typed line by line.
- Three difficulty levels (easy / medium / hard) and Turkish and English
  word pools; Turkish characters (ı ğ ş ç ö ü) are validated
  case-sensitively.
- Per-character coloring (correct / incorrect / cursor / pending) and a
  results screen with net WPM, gross WPM, accuracy and elapsed time.
- An animated Hello Kitty on the main menu that renders in any terminal;
  dark and light pink themes.

Requirements: Python 3.9+ and a terminal of at least 80x24; a network
connection is needed only for the song-lyrics mode. Quick start:

```sh
cd tui-kittytype
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kittytype
```

### youtube-terminal — YouTube in the terminal

Shell scripts that play YouTube videos directly inside the terminal
(including the VS Code integrated terminal) without a browser or GUI,
and set up shared viewing sessions. Targets macOS. See
[youtube-terminal/README.md](youtube-terminal/README.md) for details.

Included tools:

- `yt-vscode`: Plays a video in the VS Code terminal. Audio and timing
  are handled by `mpv`; frames are extracted with `ffmpeg` and rendered
  by `chafa` as colored character blocks. Audio and video are re-synced
  after seeking.
- `watch-together`: Generates a shared viewing link over the internet
  via `tmate`; the other party needs no installation.
- `watch-together-lan`: Opens a `tmux` session that a person on the same
  network joins over SSH; works without internet access.
- `ytfzf-kitty-ayar.sh` and `ytfzf-vscode-ayar.sh`: ready-made `ytfzf`
  configurations for the kitty and VS Code terminals.

Requirements and installation:

```sh
brew install yt-dlp mpv ffmpeg chafa ytfzf
brew install tmate tmux      # for watch-together
```

### Development

For the Python projects, tests and static analysis are run as follows:

```sh
pip install -e ".[dev]"
pytest          # unit tests
ruff check .    # static analysis
```

### License

The MIT License applies across the repository; see [LICENSE](LICENSE).
The license files within the individual project directories carry the
same terms.

---

Telif Hakkı (c) 2026 Elif Kaynar — bu depodaki tüm projelerin tasarımı ve
geliştirilmesi Elif Kaynar'a aittir. / Copyright (c) 2026 Elif Kaynar —
all projects in this repository are designed and developed by Elif Kaynar.
