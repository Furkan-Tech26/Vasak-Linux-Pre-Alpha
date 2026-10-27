"""Vaşak Shell systray — StatusNotifierItem placeholder."""

from gi.repository import Gtk


class Systray(Gtk.Box):
    """System tray area (right side of panel).

    Full StatusNotifierItem support can be added via python-pyqt5/qt6 or
    a dedicated libsnitch binding. This is a lightweight placeholder.
    """

    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.config = config

        icon = Gtk.Image.new_from_icon_name("notification-network-wireless-full")
        icon.set_pixel_size(16)
        self.append(icon)

        icon2 = Gtk.Image.new_from_icon_name("audio-volume-high")
        icon2.set_pixel_size(16)
        self.append(icon2)

        icon3 = Gtk.Image.new_from_icon_name("battery-full-charged")
        icon3.set_pixel_size(16)
        self.append(icon3)
