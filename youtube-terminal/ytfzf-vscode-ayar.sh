# ytfzf yapılandırması — VS Code TERMİNALİ için
# VS Code terminali kitty grafik protokolünü desteklemez, bu yüzden --vo=tct
# (renkli Unicode karakter-blokları) kullanılır. Görüntü kaba/pikselli olur
# ama VS Code terminalinin İÇİNDE oynar.
# Ayrıntı: man ytfzf(5)

# Donma çözümü (agresif): tct her kareyi karaktere çevirir, CPU yetişmezse donar.
#   240p indir -> çevrilecek veri minimum
#   ızgara 80x45 -> terminale az karakter çiz (daha hızlı)
#   --framedrop=vo + --video-sync=audio -> görüntü yetişemezse SESİ akıt, kare at
#   --vd-lavc-fast / --vd-lavc-skiploopfilter=all -> çözmeyi hızlandır
#   --cache=yes -> ağ takılmasını tamponla
url_handler_opts="--vo=tct --vo-tct-width=80 --vo-tct-height=45 --ytdl-format='bestvideo[height<=240]+bestaudio/best[height<=240]/best[height<=360]/best' --framedrop=vo --video-sync=audio --vd-lavc-fast --vd-lavc-skiploopfilter=all --cache=yes --really-quiet --profile=sw-fast"

# Küçük resim önizleme (ytfzf -t): macOS'ta chafa
thumbnail_viewer="chafa"
