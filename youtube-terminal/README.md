# youtube-terminal

> Watch, search, and **co-watch** YouTube straight from your terminal — including the VS Code integrated terminal — on macOS.

**Languages:** [English](#english) · [Türkçe](#türkçe)

No browser, no GUI. Video is rendered as colored character blocks right inside the terminal, with full keyboard control (seek, volume, pause). Includes two **watch-together** modes so you and a friend see the exact same screen at the same time.

---

<a name="english"></a>

## English

### What's inside

| Tool                  | What it does                                                                                                  |
| --------------------- | ------------------------------------------------------------------------------------------------------------ |
| `yt-vscode`           | Main tool. Plays YouTube **inside the VS Code terminal** with keyboard controls. Audio + timing via `mpv --no-video`, frames extracted with `ffmpeg`, drawn as colored blocks with `chafa`. Re-syncs audio/video on seek. |
| `watch-together`      | **Co-watch over the internet** using `tmate`. Generates a browser/SSH link your friend opens — they see your live terminal. No install needed on their side. |
| `watch-together-lan`  | **Co-watch on the same Wi-Fi** without `tmate.io`. Opens a local `tmux` session your friend joins over SSH. Works offline / LAN-only. |
| `ytfzf-kitty-ayar.sh` | `ytfzf` config for the **kitty** terminal — real video frames, best quality.                                  |
| `ytfzf-vscode-ayar.sh`| `ytfzf` config tuned for the **VS Code terminal** (`--vo=tct` character-art, aggressive anti-freeze settings). |

### How it works (`yt-vscode`)

The VS Code terminal doesn't support the sixel/kitty graphics protocol, and `mpv --vo=tct` crashes it. So this script splits the job:

- **Audio + clock + control** → `mpv --no-video` with an IPC socket (seek / pause / volume go here)
- **Video** → `ffmpeg` slices the stream into PNG frames → `chafa` draws them as colored Unicode blocks
- **On seek** → `ffmpeg` is restarted from `mpv`'s new position, so audio and video stay in sync

### Requirements

```bash
brew install yt-dlp mpv ffmpeg chafa ytfzf
brew install tmate tmux      # for watch-together
```

> `nc` (netcat) and `awk` ship with macOS.

### Install

```bash
git clone https://github.com/codedbyelif/youtube-terminal.git
cd youtube-terminal

mkdir -p ~/.local/bin ~/.config/ytfzf

# Scripts
cp yt-vscode watch-together watch-together-lan ~/.local/bin/
chmod +x ~/.local/bin/yt-vscode ~/.local/bin/watch-together ~/.local/bin/watch-together-lan

# ytfzf config — pick the one matching your terminal, copy it as conf.sh
cp ytfzf-kitty-ayar.sh  ~/.config/ytfzf/conf.sh     # if you use kitty
# cp ytfzf-vscode-ayar.sh ~/.config/ytfzf/conf.sh    # if you use the VS Code terminal

# Add ~/.local/bin to PATH (zsh)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Usage

**1) Watch in the VS Code terminal**

```bash
yt-vscode "search words"
yt-vscode "https://youtube.com/watch?v=..."
```

Keys while playing:

| Key      | Action                  |
| -------- | ----------------------- |
| ← →      | Seek 10s back / forward |
| ↑ ↓      | Volume up / down        |
| `space`  | Pause / resume          |
| `q`      | Quit                    |

Env tweaks:

```bash
YTV_WIDTH=130 yt-vscode "..."   # bigger / sharper picture
YTV_FPS=8     yt-vscode "..."   # smoother (heavier on CPU)
```

**2) Co-watch over the internet (tmate)**

```bash
watch-together
```

1. Send the printed **link** to your friend (browser link = no install).
2. Once they're connected, play a video in the session: `yt-vscode "video name"`.
3. You both see the same picture at the same time. Quit: `Ctrl+C` then `exit`.

**3) Co-watch on the same Wi-Fi (no tmate.io)**

```bash
watch-together-lan
```

Send the printed SSH command to your friend, they connect, then play with `yt-vscode`.

> **Prerequisite:** macOS *Remote Login (SSH)* must be on:
> System Settings → General → Sharing → Remote Login → **On**
> (or run `sudo systemsetup -setremotelogin on`)

**4) Sharpest playback in kitty**

```bash
ytfzf "search words"
```

Open kitty from Spotlight (`Cmd+Space` → `kitty`). Renders real video frames.

### Troubleshooting

| Symptom                          | Fix                                            |
| -------------------------------- | ---------------------------------------------- |
| `command not found`              | Open a new terminal **or** `source ~/.zshrc`   |
| YouTube won't resolve / open     | `brew upgrade yt-dlp`                           |
| Picture looks coarse in VS Code  | Expected (terminal limit). Use kitty for sharp video. |
| Picture freezes in VS Code       | Lower `YTV_WIDTH` and `YTV_FPS`                |

---

<a name="türkçe"></a>

## Türkçe

### İçindekiler

| Araç                  | Ne yapar                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------ |
| `yt-vscode`           | Ana araç. YouTube'u **VS Code terminalinde** klavye kontrolüyle oynatır. Ses + zaman `mpv --no-video` ile, kareler `ffmpeg` ile, çizim `chafa` ile yapılır. Sarınca ses/görüntü yeniden senkronlanır. |
| `watch-together`      | **İnternet üzerinden birlikte izleme** (`tmate`). Çıkan tarayıcı/SSH linkini arkadaşın açar, senin canlı terminalini görür. Karşı tarafta kurulum gerekmez. |
| `watch-together-lan`  | **Aynı wifi'da birlikte izleme** (`tmate.io` gerekmez). Yerel `tmux` oturumu açar, arkadaşın SSH ile katılır. İnternet bağımsız / yerel ağ. |
| `ytfzf-kitty-ayar.sh` | **kitty** terminali için `ytfzf` ayarı — gerçek video kareleri, en iyi kalite.                                |
| `ytfzf-vscode-ayar.sh`| **VS Code terminali** için ayarlanmış `ytfzf` ayarı (`--vo=tct` karakter-sanatı, agresif donma-önleme).       |

### Nasıl çalışır (`yt-vscode`)

VS Code terminali sixel/kitty grafik protokolünü desteklemez ve `mpv --vo=tct` onu çökertir. Bu yüzden iş ikiye bölünür:

- **Ses + saat + kontrol** → IPC soketi açık `mpv --no-video` (sarma / duraklatma / ses burada)
- **Görüntü** → `ffmpeg` akışı PNG karelere böler → `chafa` renkli Unicode bloklara çizer
- **Sarma olunca** → `ffmpeg`, `mpv`'nin yeni pozisyonundan yeniden başlatılır; ses ve görüntü senkron kalır

### Gereksinimler

```bash
brew install yt-dlp mpv ffmpeg chafa ytfzf
brew install tmate tmux      # birlikte izleme için
```

> `nc` (netcat) ve `awk` macOS'ta hazır gelir.

### Kurulum

```bash
git clone https://github.com/codedbyelif/youtube-terminal.git
cd youtube-terminal

mkdir -p ~/.local/bin ~/.config/ytfzf

# Scriptler
cp yt-vscode watch-together watch-together-lan ~/.local/bin/
chmod +x ~/.local/bin/yt-vscode ~/.local/bin/watch-together ~/.local/bin/watch-together-lan

# ytfzf ayarı — terminaline uyanı conf.sh olarak kopyala
cp ytfzf-kitty-ayar.sh  ~/.config/ytfzf/conf.sh     # kitty kullanıyorsan
# cp ytfzf-vscode-ayar.sh ~/.config/ytfzf/conf.sh    # VS Code terminali kullanıyorsan

# ~/.local/bin'i PATH'e ekle (zsh)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Kullanım

**1) VS Code terminalinde izleme**

```bash
yt-vscode "arama kelimesi"
yt-vscode "https://youtube.com/watch?v=..."
```

Oynarken tuşlar:

| Tuş      | İşlev                  |
| -------- | ---------------------- |
| ← →      | 10 sn geri / ileri sar |
| ↑ ↓      | Ses aç / kıs           |
| `boşluk` | Duraklat / devam       |
| `q`      | Çıkış                  |

Ayarlar (env):

```bash
YTV_WIDTH=130 yt-vscode "..."   # daha büyük / net görüntü
YTV_FPS=8     yt-vscode "..."   # daha akıcı (CPU'yu zorlar)
```

**2) İnternet üzerinden birlikte izleme (tmate)**

```bash
watch-together
```

1. Çıkan **linki** arkadaşına yolla (tarayıcı linki = kurulum gerekmez).
2. Arkadaşın bağlandıktan sonra oturumda video aç: `yt-vscode "video adı"`.
3. İkiniz de aynı görüntüyü aynı anda görürsünüz. Çıkış: `Ctrl+C` sonra `exit`.

**3) Aynı wifi'da birlikte izleme (tmate.io gerekmez)**

```bash
watch-together-lan
```

Çıkan SSH komutunu arkadaşına yolla, o bağlansın, sonra `yt-vscode` ile video aç.

> **Ön koşul:** Mac'te *Uzaktan Oturum Açma (Remote Login / SSH)* açık olmalı:
> Sistem Ayarları → Genel → Paylaşım → Uzaktan Oturum Açma → **AÇ**
> (veya: `sudo systemsetup -setremotelogin on`)

**4) kitty terminalinde en net izleme**

```bash
ytfzf "arama kelimesi"
```

kitty'yi Spotlight'tan aç (`Cmd+Boşluk` → `kitty`). Gerçek video kareleri çizer.

### Sorun olursa

| Belirti                          | Çözüm                                          |
| -------------------------------- | ---------------------------------------------- |
| `command not found`              | Yeni terminal aç **veya** `source ~/.zshrc`    |
| YouTube açılmıyor / çözümlenmiyor | `brew upgrade yt-dlp`                          |
| VS Code'da görüntü kaba          | Normal (terminal sınırı). Net için kitty kullan. |
| VS Code'da görüntü donuyor       | `YTV_WIDTH` ve `YTV_FPS` değerlerini düşür     |

---

## License / Lisans

[MIT](LICENSE) © [codedbyelif](https://github.com/codedbyelif)

> Educational / personal use. Respect YouTube's Terms of Service.
> Eğitim / kişisel kullanım içindir. YouTube Kullanım Koşullarına uyun.
