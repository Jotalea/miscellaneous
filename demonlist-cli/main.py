#!/usr/bin/env python3
"""
Demon Position TUI
===================
A terminal app that browses the Pointercrate Demonlist and/or the AREDL
(All-Rated Extreme Demon List), showing every level's position. Type in the
filter box to narrow the list down by name as you type.

Usage:
    python main.py

Requirements:
    pip install textual httpx

Controls:
    Start typing to filter the currently loaded list by name (live, no Enter needed).
    Tab / Shift+Tab to move between the filter box and the source selector.
    Ctrl+R refreshes the cached list data (in case positions changed).
    q quits.

APIs used:
    Pointercrate API v2  -> https://pointercrate.com/api/v2/demons/listed/
    AREDL API v2         -> https://api.aredl.net/v2/api/aredl/levels
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    RadioButton,
    RadioSet,
    Static,
)

POINTERCRATE_LISTED_URL = "https://pointercrate.com/api/v2/demons/listed/"
AREDL_LEVELS_URL = "https://api.aredl.net/v2/api/aredl/levels"

REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "demon-position-tui/1.0 (+https://pointercrate.com, https://aredl.net)",
}

SOURCE_IDS = {
    "rb_pc": "pointercrate",
    "rb_aredl": "aredl",
    "rb_both": "both",
}


@dataclass
class LevelResult:
    source: str
    position: Optional[int]
    name: str
    extra: str


def parse_next_link(link_header: Optional[str]) -> Optional[str]:
    """Parse an RFC5988-style Link/Links header and return the rel="next" URL, if any."""
    if not link_header:
        return None
    for part in link_header.split(","):
        if 'rel="next"' in part:
            start = part.find("<")
            end = part.find(">")
            if start != -1 and end != -1:
                return part[start + 1 : end]
    return None


class DemonPositionApp(App):
    """TUI for browsing demon/level positions on Pointercrate and AREDL."""

    TITLE = "Demon Position Checker"
    SUB_TITLE = "Pointercrate + AREDL"

    CSS = """
    Screen {
        align: center top;
    }

    #main {
        width: 100%;
        max-width: 110;
        height: 100%;
        padding: 1 2;
    }

    #hint {
        color: $text-muted;
        padding-bottom: 1;
    }

    #search {
        margin-bottom: 1;
    }

    RadioSet {
        layout: horizontal;
        height: auto;
        width: auto;
        margin-bottom: 1;
        border: round $primary;
        padding: 0 1;
    }

    RadioButton {
        margin-right: 2;
    }

    #results {
        height: 1fr;
        border: round $primary;
    }

    #status {
        padding-top: 1;
        color: $text-muted;
        height: auto;
    }
    """

    BINDINGS = [
        ("ctrl+r", "refresh_cache", "Refresh cached lists"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._pointercrate_cache: Optional[list[dict]] = None
        self._aredl_cache: Optional[list[dict]] = None
        self._selected_source: str = "pointercrate"
        self._all_results: list[LevelResult] = []
        self._current_filter: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main"):
            yield Static(
                "Full list loads automatically. Start typing to filter by name — "
                "no need to press Enter.",
                id="hint",
            )
            yield Input(
                placeholder="Filter by name (optional), e.g. Tartarus...",
                id="search",
            )
            with RadioSet(id="source"):
                yield RadioButton("Pointercrate", value=True, id="rb_pc")
                yield RadioButton("AREDL", id="rb_aredl")
                yield RadioButton("Both", id="rb_both")
            yield DataTable(id="results")
            yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results", DataTable)
        table.add_columns("List", "Position", "Level", "Details")
        table.cursor_type = "row"
        table.zebra_stripes = True
        self.query_one("#search", Input).focus()
        self.load_and_display()

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        button_id = event.pressed.id
        if button_id in SOURCE_IDS and SOURCE_IDS[button_id] != self._selected_source:
            self._selected_source = SOURCE_IDS[button_id]
            self.load_and_display()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self._current_filter = event.value.strip()
            self._apply_filter()

    def action_refresh_cache(self) -> None:
        self._pointercrate_cache = None
        self._aredl_cache = None
        self.load_and_display()

    # ------------------------------------------------------------------
    # Networking
    # ------------------------------------------------------------------

    async def _fetch_pointercrate(self) -> list[dict]:
        if self._pointercrate_cache is not None:
            return self._pointercrate_cache

        demons: list[dict] = []
        async with httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=20) as client:
            url = POINTERCRATE_LISTED_URL
            params: Optional[dict] = {"limit": 100}
            while url:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                page = resp.json()
                if isinstance(page, list):
                    demons.extend(page)
                link_header = resp.headers.get("Links") or resp.headers.get("Link")
                url = parse_next_link(link_header)
                params = None  # next URL already carries its own query params

        self._pointercrate_cache = demons
        return demons

    async def _fetch_aredl(self) -> list[dict]:
        if self._aredl_cache is not None:
            return self._aredl_cache

        async with httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=30) as client:
            resp = await client.get(AREDL_LEVELS_URL, params={"exclude_legacy": "false"})
            resp.raise_for_status()
            data = resp.json()

        self._aredl_cache = data if isinstance(data, list) else []
        return self._aredl_cache

    # ------------------------------------------------------------------
    # Loading + filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _pointercrate_to_results(demons: list[dict]) -> list[LevelResult]:
        results = []
        for demon in demons:
            requirement = demon.get("requirement")
            extra = f"{requirement}% required" if requirement is not None else ""
            results.append(
                LevelResult(
                    source="Pointercrate",
                    position=demon.get("position"),
                    name=demon.get("name", ""),
                    extra=extra,
                )
            )
        return results

    @staticmethod
    def _aredl_to_results(levels: list[dict]) -> list[LevelResult]:
        results = []
        for level in levels:
            points = level.get("points")
            legacy = level.get("legacy")
            bits = []
            if points is not None:
                bits.append(f"{points} pts")
            if legacy:
                bits.append("legacy")
            results.append(
                LevelResult(
                    source="AREDL",
                    position=level.get("position"),
                    name=level.get("name", ""),
                    extra=" · ".join(bits),
                )
            )
        return results

    @work(exclusive=True)
    async def load_and_display(self) -> None:
        source = self._selected_source
        table = self.query_one("#results", DataTable)
        table.loading = True
        self._set_status("Loading list(s)...")

        results: list[LevelResult] = []
        errors: list[str] = []

        if source in ("pointercrate", "both"):
            try:
                results += self._pointercrate_to_results(await self._fetch_pointercrate())
            except httpx.HTTPError as exc:
                errors.append(f"Pointercrate: {exc}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Pointercrate: unexpected error ({exc})")

        if source in ("aredl", "both"):
            try:
                results += self._aredl_to_results(await self._fetch_aredl())
            except httpx.HTTPError as exc:
                errors.append(f"AREDL: {exc}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"AREDL: unexpected error ({exc})")

        def sort_key(r: LevelResult):
            return (r.source, r.position if r.position is not None else 10**9)

        results.sort(key=sort_key)
        self._all_results = results
        table.loading = False

        if errors:
            self._set_status("[red]" + " | ".join(errors) + "[/red]")

        self._apply_filter()

    def _apply_filter(self) -> None:
        table = self.query_one("#results", DataTable)
        table.clear()

        needle = self._current_filter.lower()
        if needle:
            visible = [r for r in self._all_results if needle in r.name.lower()]
        else:
            visible = self._all_results

        rows = [
            (
                r.source,
                str(r.position) if r.position is not None else "—",
                r.name,
                r.extra,
            )
            for r in visible
        ]
        if rows:
            table.add_rows(rows)

        total = len(self._all_results)
        if needle:
            self._set_status(f"{len(visible)} match(es) for '{self._current_filter}' out of {total} loaded.")
        else:
            self._set_status(f"Showing all {total} level(s).")


def main() -> None:
    DemonPositionApp().run()


if __name__ == "__main__":
    main()
