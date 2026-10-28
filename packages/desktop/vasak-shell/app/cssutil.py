"""CSS loading helper compatible across GTK4 minor versions."""

from gi.repository import Gtk, Gdk


def css_rgba(color, default_alpha=1.0):
    """Format a config color as a valid GTK CSS ``rgba()`` value.

    Vaşak config stores colors as normalized floats (0..1), but GTK CSS
    expects channel values in 0..255. Colors already in 0..255 are passed
    through unchanged, so hand-edited user configs keep working.
    """
    values = list(color) if color is not None else [1.0, 1.0, 1.0, default_alpha]
    while len(values) < 4:
        values.append(default_alpha)
    r, g, b, a = values[:4]
    if max(r, g, b) <= 1.0:
        r, g, b = r * 255.0, g * 255.0, b * 255.0
    return "rgba(%d, %d, %d, %s)" % (
        round(r),
        round(g),
        round(b),
        round(float(a), 3),
    )


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
