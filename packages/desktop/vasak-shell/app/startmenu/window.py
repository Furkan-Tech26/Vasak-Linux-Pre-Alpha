"""Vaşak Shell start menu — Windows 8.1 style full-screen live tile overlay."""

from gi.repository import Gtk, Gdk

from layer import GdkLayerShell, HAS_LAYER_SHELL
from cssutil import load_css

from startmenu.tile_grid import TileGrid
from startmenu.search import SearchEntry
from startmenu.group_bar import GroupBar


class StartMenuWindow(Gtk.Window):
    """Full-screen start menu with live tiles and named groups (Win 8.1 style)."""

    def __init__(self, config):
        super().__init__()

        self.config = config
        menu_cfg = config.startmenu()

        self.set_title("Vaşak Menu")
        self.set_decorated(False)
        self.set_default_size(1280, 800)

        # Layer-shell only makes sense for the full-screen (Win 8.1) mode
        use_layer = HAS_LAYER_SHELL and menu_cfg.get("fullscreen", True)
        if use_layer:
            GdkLayerShell.init_for_window(self)
            GdkLayerShell.set_layer(self, GdkLayerShell.Layer.OVERLAY)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.TOP, True)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.BOTTOM, True)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.LEFT, True)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.RIGHT, True)
            GdkLayerShell.set_keyboard_interactivity(self, True)
            GdkLayerShell.set_exclusive_zone(self, -1)
        elif menu_cfg.get("fullscreen", True):
            self.fullscreen()

        # Main vertical layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(box)

        # Top bar: search + user/profile
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        top_bar.set_margin_top(24)
        top_bar.set_margin_start(32)
        top_bar.set_margin_end(32)
        top_bar.set_margin_bottom(16)

        self.search = SearchEntry()
        self.search.set_hexpand(True)
        top_bar.append(self.search)

        # User pill (right side)
        user_pill = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        user_pill.set_halign(Gtk.Align.END)
        user_pill.set_hexpand(False)
        avatar = Gtk.Image.new_from_icon_name("avatar-default-symbolic")
        avatar.set_pixel_size(32)
        user_pill.append(avatar)
        name_lbl = Gtk.Label(label="User")
        name_lbl.add_css_class("startmenu-user")
        user_pill.append(name_lbl)
        top_bar.append(user_pill)

        box.append(top_bar)

        # Group bar (like Win 8.1 group labels)
        self.group_bar = GroupBar(config)
        box.append(self.group_bar)

        # Tile grid (scrollable)
        self.grid = TileGrid(config)
        box.append(self.grid)

        # Wire group filter and search to the grid
        self.group_bar.set_grid_filter_callback(self.grid.set_group_filter)
        self.search.connect(
            "search-changed", lambda entry: self.grid.set_search_filter(entry.get_text())
        )

        # Bottom hint
        hint = Gtk.Label(label="Press Esc to close  •  Right-click a tile to customize")
        hint.add_css_class("startmenu-hint")
        hint.set_margin_bottom(16)
        hint.set_halign(Gtk.Align.CENTER)
        box.append(hint)

        # Close on Escape (GTK4 event controller)
        key_ctrl = Gtk.EventControllerKey.new()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_ctrl)

        # Apply glass CSS
        self._apply_css(menu_cfg)

    def _apply_css(self, menu_cfg):
        bg = menu_cfg["bg_rgba"]
        load_css(
            f"""
            window {{
                background-color: rgba({bg[0]}, {bg[1]}, {bg[2]}, {bg[3]});
                color: white;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
            }}
            .startmenu-user {{
                color: rgba(255,255,255,0.85);
                font-weight: 600;
                font-size: 14px;
            }}
            .startmenu-hint {{
                color: rgba(255,255,255,0.5);
                font-size: 12px;
            }}
            .group-label {{
                color: rgba(255,255,255,0.7);
                font-weight: 700;
                font-size: 16px;
                letter-spacing: 1px;
            }}
            """
        )

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if Gdk.keyval_name(keyval) == "Escape":
            self.hide()
            return True
        return False
