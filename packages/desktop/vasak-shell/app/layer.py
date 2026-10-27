"""Layer-shell availability helper.

gtk4-layer-shell provides the Gtk4LayerShell typelib. If it is not installed
(or we're not on Wayland), the shell falls back to regular windows so it still
runs for development/testing.
"""

import gi

try:
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk4LayerShell as GdkLayerShell  # type: ignore
    HAS_LAYER_SHELL = True
except (ImportError, ValueError):
    GdkLayerShell = None
    HAS_LAYER_SHELL = False
