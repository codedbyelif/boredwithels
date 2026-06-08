"""Hedef metni gosteren ve yazilani karakter karakter renklendiren widget.

Input DEGIL: can_focus=True bir Widget + on_key. Cunku sabit hedef metni
karakter karakter durumlandirmak bir 'render' problemidir, duzenleme alani degil.
Renkler aktif temadan turetilir (char_styles), boylece koyu/acik temada okunakli kalir.
"""
from __future__ import annotations

from rich.text import Text
from textual import events
from textual.message import Message
from textual.widget import Widget

from kittytype.core.engine import TypingEngine
from kittytype.theme import char_styles


class TypingArea(Widget):
    can_focus = True

    class Progress(Message):
        """Her tus vurusunda yayinlanir (canli istatistik / sayac icin)."""

        def __init__(self, first_keystroke: bool) -> None:
            super().__init__()
            self.first_keystroke = first_keystroke

    class Completed(Message):
        """Hedef metin tamamen yazildiginda yayinlanir (sarki modunda testi bitirir)."""

    def __init__(self, target: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.engine = TypingEngine(target)
        self._started = False
        self._frozen = False

    def on_mount(self) -> None:
        self.focus()

    def freeze(self) -> None:
        """Sure dolunca / test bitince girisleri durdur."""
        self._frozen = True

    def render(self) -> Text:
        engine = self.engine
        cursor = engine.cursor
        styles = char_styles(self.app.current_theme)
        text = Text()
        for i, ch in enumerate(engine.target):
            at_cursor = i == cursor and not self._frozen
            if ch == "\n":
                # Satir sonu: imlec buradaysa kucuk bir isaret goster, sonra satiri kir.
                if at_cursor:
                    text.append("↵", style=styles["cursor"])
                text.append("\n")
                continue
            style = styles["cursor"] if at_cursor else styles[engine.status_at(i).value]
            text.append(ch, style=style)
        return text

    def on_key(self, event: events.Key) -> None:
        if self._frozen:
            return

        if event.key == "backspace":
            self.engine.backspace()
            event.stop()
            self.refresh()
            if self._started:
                self.post_message(self.Progress(first_keystroke=False))
            self._scroll_to_cursor()
            return

        if self.engine.is_complete:
            return

        ch = event.character
        if event.key == "space":
            ch = " "
        elif event.key == "enter":
            cur = self.engine.cursor
            target = self.engine.target
            if cur < len(target) and target[cur] == "\n":
                ch = "\n"  # satir sonunda Enter de kabul (Space da olur)
            else:
                return
        elif ch is None or len(ch) != 1 or not ch.isprintable():
            return  # ok tuslari, ctrl, fn vb. yoksay

        self.engine.type_char(ch)
        event.stop()
        first = not self._started
        self._started = True
        self.refresh()
        self.post_message(self.Progress(first_keystroke=first))
        self._scroll_to_cursor()
        if self.engine.is_complete:
            self.post_message(self.Completed())

    def _scroll_to_cursor(self) -> None:
        """Imleci, ust kaydirilabilir kapsayicida gorunur tut (yaklasik)."""
        parent = self.parent
        if parent is None or not hasattr(parent, "scroll_to"):
            return
        width = self.content_size.width
        view_height = getattr(parent, "content_size", self.size).height
        if width <= 0 or view_height <= 0:
            return
        prefix = self.engine.target[: self.engine.cursor]
        if not prefix:
            parent.scroll_to(y=0, animate=False)
            return
        try:
            rows = len(Text(prefix).wrap(self.app.console, width))
        except Exception:
            return
        target_y = max(0, rows - 1 - view_height // 2)
        parent.scroll_to(y=target_y, animate=False)
