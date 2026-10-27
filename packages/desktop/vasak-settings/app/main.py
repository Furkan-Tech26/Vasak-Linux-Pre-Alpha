"""Vaşak Settings entry point — GTK4/libadwaita settings window."""

import os
import signal
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

from gi.repository import Gtk, Gdk, Adw

from window import SettingsWindow


def load_settings_css():
    """Load the settings stylesheet from the install dir (or source tree)."""
    candidates = [
        "/usr/share/vasak-settings/data/settings.css",
        os.path.join(os.path.dirname(__file__), "..", "data", "settings.css"),
    ]
    for path in candidates:
        if os.path.exists(path):
            provider = Gtk.CssProvider()
            try:
                provider.load_from_path(path)
            except Exception:
                return
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            return


def main():
    app = Adw.Application(application_id="org.vasak.settings")

    def on_activate(app):
        load_settings_css()
        SettingsWindow(app).present()

    app.connect("activate", on_activate)
    app.run(sys.argv)


if __name__ == "__main__":
    main()
