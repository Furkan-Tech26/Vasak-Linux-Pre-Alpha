"""Bluetooth page."""

from gi.repository import Gtk, Adw


class BluetoothPage(Adw.NavigationPage):
    def __init__(self):
        super().__init__()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_bottom(24)
        lbl = Gtk.Label()
        lbl.set_markup("<b>Bluetooth</b>\nPair and manage Bluetooth devices (blueman/bluez).")
        lbl.set_halign(Gtk.Align.START)
        box.append(lbl)
        self.set_child(box)
