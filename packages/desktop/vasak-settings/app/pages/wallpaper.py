"""Wallpaper page — pick desktop background."""

from gi.repository import Gtk, Adw


class WallpaperPage(Adw.NavigationPage):
    def __init__(self):
        super().__init__()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_bottom(24)

        lbl = Gtk.Label()
        lbl.set_markup("<b>Wallpaper</b>\nChoose a background from /usr/share/backgrounds/vasak/")
        lbl.set_halign(Gtk.Align.START)
        box.append(lbl)

        thumb = Gtk.Image.new_from_icon_name("preferences-desktop-wallpaper-symbolic")
        thumb.set_pixel_size(120)
        box.append(thumb)

        self.set_child(box)
