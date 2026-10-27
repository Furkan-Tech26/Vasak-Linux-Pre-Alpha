"""Vaşak Shell clock — shows date/time in the panel."""

import time

from gi.repository import Gtk, GLib


class Clock(Gtk.Label):
    """Updating clock label."""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.add_css_class("panel-clock")
        self._update()
        # Update every second
        GLib.timeout_add_seconds(1, self._update)

    def _update(self):
        self.set_label(time.strftime("%H:%M  %a, %d %b"))
        return True  # keep timeout running
