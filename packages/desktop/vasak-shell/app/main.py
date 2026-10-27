"""Vaşak Shell entry point — launches the panel and full-screen start menu."""

import os
import sys
import signal

# gtk4-layer-shell must be linked before libwayland-client (see its README).
try:
    from ctypes import CDLL
    for _lib in ("libgtk4-layer-shell.so.0", "libgtk4-layer-shell.so"):
        try:
            CDLL(_lib)
            break
        except OSError:
            continue
except Exception:
    pass

from gi.repository import GLib, Gtk, Gdk

# Allow Ctrl+C to quit cleanly
signal.signal(signal.SIGINT, signal.SIG_DFL)

from panel.window import PanelWindow
from startmenu.window import StartMenuWindow


def load_styles():
    """Load shipped shell.css + user override (~/.config/vasak-shell/user.css)."""
    candidates = [
        "/usr/share/vasak-shell/data/shell.css",
        os.path.join(os.path.dirname(__file__), "..", "data", "shell.css"),
    ]
    for path in candidates:
        if os.path.exists(path):
            provider = Gtk.CssProvider()
            try:
                provider.load_from_path(path)
                display = Gdk.Display.get_default()
                if display is not None:
                    Gtk.StyleContext.add_provider_for_display(
                        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                    )
            except Exception:
                pass
            break

    # User override wins over everything
    user_css = os.path.expanduser("~/.config/vasak-shell/user.css")
    if os.path.exists(user_css):
        provider = Gtk.CssProvider()
        try:
            provider.load_from_path(user_css)
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
                )
        except Exception:
            pass


def main():
    """Initialize GTK, create the panel + start menu, run the main loop."""
    Gtk.init()

    from config import ShellConfig
    config = ShellConfig.load()

    load_styles()

    # Top panel (layer-shell)
    panel = PanelWindow(config)

    # Full-screen start menu (hidden by default)
    startmenu = StartMenuWindow(config)
    startmenu.hide()

    # App menu button toggles the full-screen start menu
    panel.app_menu_button.connect("clicked", lambda *_: toggle_startmenu(startmenu))

    panel.present()
    GLib.MainLoop().run()


def toggle_startmenu(startmenu):
    """Show/hide the full-screen start menu."""
    if startmenu.get_visible():
        startmenu.hide()
    else:
        startmenu.present()


if __name__ == "__main__":
    main()
