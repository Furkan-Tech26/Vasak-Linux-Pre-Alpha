"""Sound page."""

from gi.repository import Gtk, Adw


class SoundPage(Adw.NavigationPage):
    def __init__(self):
        super().__init__()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_bottom(24)
        lbl = Gtk.Label()
        lbl.set_markup("<b>Sound</b>\nVolume, input/output devices (PipeWire).")
        lbl.set_halign(Gtk.Align.START)
        box.append(lbl)
        self.set_child(box)
