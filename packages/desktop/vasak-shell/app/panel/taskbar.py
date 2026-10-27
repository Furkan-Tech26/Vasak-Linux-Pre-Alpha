"""Vaşak Shell taskbar — lists open windows."""

from gi.repository import Gtk


class Taskbar(Gtk.Box):
    """Center taskbar showing active window title and window switches."""

    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.config = config

        self.label = Gtk.Label(label="Vaşak Linux")
        self.label.set_hexpand(False)
        self.label.add_css_class("taskbar-title")
        self.append(self.label)

        # Window list placeholder (would integrate with layer-shell / wlr layer)
        self.windows_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.append(self.windows_box)

    def set_active_title(self, title: str):
        self.label.set_label(title or "Vaşak Linux")
