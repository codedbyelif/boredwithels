"""Sarki sozu arama ekrani (LRCLIB, async worker)."""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, ListItem, ListView, Static

from kittytype.config import Mode, TestConfig
from kittytype.core.text_source import prepare_lyrics
from kittytype.lyrics import client as lyrics_client
from kittytype.lyrics.models import LrclibTrack


class TrackItem(ListItem):
    def __init__(self, track: LrclibTrack) -> None:
        super().__init__(Static(track.display))
        self.track = track


class SongSearchScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Geri")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="search"):
            yield Static("🎵  Şarkı Sözü Ara", classes="title")
            yield Input(placeholder="Şarkı veya sanatçı ara… (Enter)", id="query")
            yield Static("Bir şarkı arayın.", id="search-status")
            yield ListView(id="results")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#query", Input).focus()

    def _status(self, msg: str) -> None:
        self.query_one("#search-status", Static).update(msg)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if query:
            self._status("Aranıyor…")
            self.search_lyrics(query)

    @work(exclusive=True, group="lrclib")
    async def search_lyrics(self, query: str) -> None:
        try:
            tracks = await lyrics_client.search(query)
        except lyrics_client.LrclibError:
            self._status("Bağlantı hatası. Tekrar deneyin.")
            return
        results = self.query_one("#results", ListView)
        await results.clear()
        if not tracks:
            self._status("Sonuç bulunamadı.")
            return
        self._status(f"{len(tracks)} sonuç — yazmak için seçin (↑↓ + Enter).")
        for track in tracks[:30]:
            await results.append(TrackItem(track))
        results.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, TrackItem) or not item.track.plain_lyrics:
            return
        text = prepare_lyrics(item.track.plain_lyrics)
        if not text:
            self._status("Bu şarkının sözleri boş.")
            return
        config = TestConfig(mode=Mode.LYRICS, song_title=item.track.display)

        from kittytype.screens.typing import TypingScreen

        self.app.switch_screen(TypingScreen(text=text, config=config))
