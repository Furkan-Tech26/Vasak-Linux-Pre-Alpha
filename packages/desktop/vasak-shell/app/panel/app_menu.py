"""Vaşak Shell app menu button — opens the start menu."""

from gi.repository import Gtk, GdkPixbuf


class AppMenuButton(Gtk.Button):
    """Vaşak logo button that opens the start menu."""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.set_has_tooltip(True)
        self.set_tooltip_text("Vaşak Menu")

        # Try to load the Vaşak logo icon
        icon = self._load_icon("vasak-logo", 24)
        if icon:
            self.set_child(icon)
        else:
            self.set_label("Vaşak")

        self.add_css_class("app-menu-button")

    def _load_icon(self, name, size):
        candidates = [
            f"/usr/share/pixmaps/{name}.svg",
            f"/usr/share/icons/hicolor/scalable/apps/{name}.svg",
        ]
        for path in candidates:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
                return Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception:
                continue
        return None
