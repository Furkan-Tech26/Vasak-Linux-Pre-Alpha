"""Vaşak Shell start menu tile — Windows 8.1 style live tile."""

import shlex
import subprocess

from gi.repository import Gtk, GLib

from cssutil import load_css, css_rgba

# Win 8.1 tile size hints in grid columns/rows
TILE_SIZES = {
    "small":  (1, 1),
    "medium": (1, 1),
    "wide":   (2, 1),
    "large":  (2, 2),
}

# Pixel sizes per tile type (approx, Win 8.1 metro proportions)
TILE_PIXELS = {
    "small":  (88, 88),
    "medium": (140, 140),
    "wide":   (288, 140),
    "large":  (288, 288),
}


class AppTile(Gtk.Box):
    """A live tile: colored square, icon, label, optional rotating content."""

    def __init__(self, app, group_color=None, on_resize=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.app = app
        self.size = app.get("size", "medium")
        self.group_color = group_color or [0.39, 0.40, 0.95, 1.0]
        self.on_resize = on_resize
        self.live_label = None
        self._live_timeout = None

        w, h = TILE_PIXELS.get(self.size, TILE_PIXELS["medium"])
        self.set_size_request(w, h)
        self.set_hexpand(False)
        self.set_vexpand(False)
        self.add_css_class("live-tile")
        self.add_css_class(f"tile-{self.size}")

        # Container for tile content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_hexpand(True)
        content.set_vexpand(True)
        self.append(content)

        # Icon
        icon = Gtk.Image.new_from_icon_name(app.get("icon", "application-x-executable"))
        icon.set_pixel_size(40)
        icon.set_halign(Gtk.Align.START)
        icon.set_valign(Gtk.Align.START)
        content.append(icon)

        # Label at bottom
        label = Gtk.Label(label=app["name"])
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.END)
        label.set_vexpand(True)
        label.add_css_class("live-tile-label")
        content.append(label)

        # Live tile content (rotating snippet) if enabled
        if app.get("live", False):
            self.live_label = Gtk.Label(label=app.get("live_text", "Live"))
            self.live_label.add_css_class("live-tile-content")
            self.live_label.set_halign(Gtk.Align.START)
            self.live_label.set_valign(Gtk.Align.END)
            content.append(self.live_label)
            self._live_timeout = GLib.timeout_add_seconds(5, self._rotate_live)

        # Click to launch
        self.set_cursor_from_name("pointer")
        click = Gtk.GestureClick.new()
        click.set_button(1)
        click.connect("pressed", lambda *_: self._launch())
        self.add_controller(click)

        # Right-click context menu for customization
        right_click = Gtk.GestureClick.new()
        right_click.set_button(3)
        right_click.connect("pressed", self._on_right_click)
        self.add_controller(right_click)

        self._apply_css()

    def _apply_css(self):
        c = self.group_color
        base = css_rgba(c)
        active = css_rgba([c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, c[3]])
        # Unique class per tile: a shared .live-tile background rule would make
        # every tile inherit the last-created provider's color.
        self._color_class = f"tile-color-{id(self)}"
        self.add_css_class(self._color_class)
        load_css(
            f"""
            .{self._color_class} {{
                background-color: {base};
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}
            .{self._color_class}:hover {{
                border-color: rgba(255, 255, 255, 0.5);
            }}
            .{self._color_class}:active {{
                background-color: {active};
            }}
            """
        )

    def _launch(self):
        try:
            subprocess.Popen(shlex.split(self.app["exec"]))
        except Exception as e:
            print(f"[vasak-shell] Failed to launch {self.app['name']}: {e}")
            return

        # Win 8.1 behaviour: launching an app closes the start menu.
        root = self.get_root()
        if isinstance(root, Gtk.Window):
            root.hide()

    def _rotate_live(self):
        """Rotate live tile text (simple demo behavior)."""
        if self.live_label is None:
            return False
        texts = self.app.get("live_cycle", ["Live", "Updates", "Now"])
        current = self.live_label.get_label()
        idx = texts.index(current) + 1 if current in texts else 0
        self.live_label.set_label(texts[idx % len(texts)])
        return True

    def _on_right_click(self, gesture, n_press, x, y):
        from gi.repository import Gdk

        menu = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)

        for label in ("Small", "Medium", "Wide", "Large"):
            btn = Gtk.Button(label=label)
            btn.add_css_class("flat")
            btn.connect("clicked", lambda *_, s=label.lower(): self._set_size(s, menu))
            box.append(btn)

        menu.set_child(box)
        menu.set_parent(self)
        menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        menu.connect("closed", lambda m: m.unparent())
        menu.popup()

    def _set_size(self, size, menu):
        menu.popdown()
        # Persist to config via the shell config module
        from config import ShellConfig
        cfg = ShellConfig.load()
        for app in cfg.apps():
            if app["name"] == self.app["name"]:
                app["size"] = size
                break
        cfg.save()
        if self.on_resize is not None:
            GLib.idle_add(self.on_resize)
        print(f"[vasak-shell] Set {self.app['name']} tile size to {size}")
