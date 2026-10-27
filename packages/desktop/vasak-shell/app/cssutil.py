"""CSS loading helper compatible across GTK4 minor versions."""

from gi.repository import Gtk, Gdk


def load_css(css_text, priority=Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION):
    """Load a CSS string into the default display."""
    provider = Gtk.CssProvider()
    try:
        # GTK >= 4.12
        provider.load_from_string(css_text)
    except AttributeError:
        provider.load_from_data(css_text.encode("utf-8"))

    display = Gdk.Display.get_default()
    if display is not None:
        Gtk.StyleContext.add_provider_for_display(display, provider, priority)
    return provider
