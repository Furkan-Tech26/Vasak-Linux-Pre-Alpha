"""Vaşak Shell blur helper — glassmorphism backdrop support.

GTK4 does not expose a simple "blur behind" API. Real blur on Wayland
requires compositor support (layer-shell + wlr-unstable-layer-v1 or
gtk-layer-shell with exclusive zone). This module documents the hook
and provides a no-op so imports don't break.
"""


def apply_blur(widget):
    """Attempt to enable backdrop blur on a GTK widget.

    Currently a no-op placeholder. On a labwc/Wayland session with
    blur enabled in labwc config, translucent panels will blur
    automatically via the compositor.
    """
    try:
        widget.set_opacity(0.92)
    except Exception:
        pass
