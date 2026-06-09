# ytfzf yapılandırması — Terminalden YouTube
# Ayrıntı: man ytfzf(5)

# --- Videoyu terminalin İÇİNDE oynat (kitty terminalinde gerçek görüntü) ---
# url_handler_opts, ytfzf'nin mpv'ye geçirdiği ekstra bayraklardır.
# --vo=kitty  -> kitty/WezTerm'de gerçek video kareleri (terminal içinde)
# --profile=sw-fast -> yazılım çözücüyle akıcı oynatma
url_handler_opts="--vo=kitty --profile=sw-fast"

# NOT: kitty yerine macOS Terminal.app'te çalıştırırsan bunu şununla değiştir:
#   url_handler_opts="--vo=tct --really-quiet --profile=sw-fast"
# (Terminal.app gerçek görüntü çizemez; kaba renkli karakter-sanatı verir.)

# --- Küçük resim (thumbnail) önizleme: macOS'ta chafa ---
# ytfzf -t ile arama yapınca fzf içinde küçük resimleri chafa render eder.
thumbnail_viewer="chafa"

# --- Tercihler ---
# Varsayılan video kalitesi tercihi (gerekirse aç):
#ytdl_pref="bestvideo[height<=720]+bestaudio/best"
