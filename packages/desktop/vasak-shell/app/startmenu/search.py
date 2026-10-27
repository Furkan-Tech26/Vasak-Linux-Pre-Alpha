"""Vaşak Shell start menu search entry."""

from gi.repository import Gtk


class SearchEntry(Gtk.SearchEntry):
    """Search bar at the top of the start menu."""

    def __init__(self):
        super().__init__()
        self.set_placeholder_text("Search apps…")
        self.set_hexpand(True)
        self.set_margin_top(12)
        self.set_margin_bottom(8)
        self.set_margin_start(16)
        self.set_margin_end(16)
