"""Vaşak Shell top panel (GTK4 layer-shell)."""

from gi.repository import Gtk

from layer import GdkLayerShell, HAS_LAYER_SHELL
from cssutil import load_css

from panel.app_menu import AppMenuButton
from panel.taskbar import Taskbar
from panel.clock import Clock
from panel.systray import Systray


class PanelWindow(Gtk.Window):
    """Top bar panel anchored to the top edge via layer-shell."""

    def __init__(self, config):
        super().__init__()

        self.config = config
        panel_cfg = config.panel()
        self.set_size_request(-1, panel_cfg["height"])

        # Layer-shell setup (Wayland); gracefully skip otherwise
        if HAS_LAYER_SHELL:
            GdkLayerShell.init_for_window(self)
            GdkLayerShell.set_layer(self, GdkLayerShell.Layer.TOP)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.TOP, True)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.LEFT, True)
            GdkLayerShell.set_anchor(self, GdkLayerShell.Edge.RIGHT, True)
            GdkLayerShell.set_margin(self, GdkLayerShell.Edge.TOP, panel_cfg["margin"])
            GdkLayerShell.set_margin(self, GdkLayerShell.Edge.LEFT, panel_cfg["margin"])
            GdkLayerShell.set_margin(self, GdkLayerShell.Edge.RIGHT, panel_cfg["margin"])
            GdkLayerShell.set_exclusive_zone(self, panel_cfg["height"] + panel_cfg["margin"])

        self.set_title("Vaşak Panel")
        self.set_decorated(False)
        self.set_resizable(False)

        # Main horizontal box
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.box.set_margin_start(12)
        self.box.set_margin_end(12)
        self.box.set_margin_top(4)
        self.box.set_margin_bottom(4)
        self.set_child(self.box)

        # App menu button (opens start menu)
        self.app_menu_button = AppMenuButton(config)
        self.box.append(self.app_menu_button)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_valign(Gtk.Align.CENTER)
        self.box.append(sep)

        # Taskbar (center)
        self.taskbar = Taskbar(config)
        self.box.append(self.taskbar)

        # Right side: systray + clock
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        right_box.set_halign(Gtk.Align.END)
        right_box.set_hexpand(True)

        self.systray = Systray(config)
        right_box.append(self.systray)

        self.clock = Clock(config)
        right_box.append(self.clock)

        self.box.append(right_box)

        # Apply glassmorphism CSS
        self._apply_css(panel_cfg)

    def _apply_css(self, panel_cfg):
        bg = panel_cfg["bg_rgba"]
        border = panel_cfg["border_color"]
        load_css(
            f"""
            window {{
                background-color: rgba({bg[0]}, {bg[1]}, {bg[2]}, {bg[3]});
                border: 1px solid rgba({border[0]}, {border[1]}, {border[2]}, {border[3]});
                border-radius: {panel_cfg['corner_radius']}px;
            }}
            """
        )
