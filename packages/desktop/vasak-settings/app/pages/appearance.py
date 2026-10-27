"""Appearance page — theme variant, accent, glass intensity, radius (saves live)."""

from gi.repository import Gtk, Adw, Gdk

import shellconfig


class AppearancePage(Adw.NavigationPage):
    def __init__(self):
        super().__init__()
        self.cfg = shellconfig.load()

        # We wrap an Adw.PreferencesPage (which is a widget) in this nav page
        page = Adw.PreferencesPage()
        self.set_child(page)

        # --- Theme variant ---
        group = Adw.PreferencesGroup()
        group.set_title("Theme")
        group.set_description("Controls the Vaşak Glass look across the desktop.")
        page.add(group)

        row = Adw.ActionRow()
        row.set_title("Variant")
        row.set_subtitle("Dark, light, or pure glass")
        self.variant_drop = Gtk.DropDown.new_from_strings(["Dark", "Light", "Glass"])
        variants = ["dark", "light", "glass"]
        current = self.cfg["theme"].get("variant", "dark")
        if current in variants:
            self.variant_drop.set_selected(variants.index(current))
        self.variant_drop.connect("notify::selected", self._on_variant)
        row.add_suffix(self.variant_drop)
        group.add(row)

        # --- Accent color ---
        accent_row = Adw.ActionRow()
        accent_row.set_title("Accent color")
        accent_row.set_subtitle("Used for tiles, buttons, highlights")
        self.accent_btn = Gtk.ColorButton.new()
        self.accent_btn.set_rgba(self._parse_hex(self.cfg["theme"].get("accent", "#6366f1")))
        self.accent_btn.connect("color-set", self._on_accent)
        accent_row.add_suffix(self.accent_btn)
        group.add(accent_row)

        # --- Glass intensity ---
        glass_row = Adw.ActionRow()
        glass_row.set_title("Glass intensity")
        glass_row.set_subtitle("Panel/menu translucency")
        self.glass_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.05)
        self.glass_scale.set_value(self.cfg["theme"].get("glass_intensity", 0.82))
        self.glass_scale.set_hexpand(True)
        self.glass_scale.connect("value-changed", self._on_glass)
        glass_row.add_suffix(self.glass_scale)
        group.add(glass_row)

        # --- Corner radius ---
        radius_row = Adw.ActionRow()
        radius_row.set_title("Corner radius")
        radius_row.set_subtitle("0 = sharp (Win 8.1), 24 = very round")
        self.radius_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 24, 1)
        self.radius_scale.set_value(self.cfg["theme"].get("radius", 12))
        self.radius_scale.set_hexpand(True)
        self.radius_scale.connect("value-changed", self._on_radius)
        radius_row.add_suffix(self.radius_scale)
        group.add(radius_row)

        # --- Panel group ---
        panel_group = Adw.PreferencesGroup()
        panel_group.set_title("Panel")
        page.add(panel_group)

        height_row = Adw.ActionRow()
        height_row.set_title("Panel height")
        self.height_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 24, 64, 2)
        self.height_scale.set_value(self.cfg["panel"].get("height", 36))
        self.height_scale.set_hexpand(True)
        self.height_scale.connect("value-changed", self._on_height)
        height_row.add_suffix(self.height_scale)
        panel_group.add(height_row)

        margin_row = Adw.ActionRow()
        margin_row.set_title("Panel margin")
        self.margin_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 24, 1)
        self.margin_scale.set_value(self.cfg["panel"].get("margin", 6))
        self.margin_scale.set_hexpand(True)
        self.margin_scale.connect("value-changed", self._on_margin)
        margin_row.add_suffix(self.margin_scale)
        panel_group.add(margin_row)

    # --- Save helpers ---

    def _flush(self):
        shellconfig.save(self.cfg)

    def _on_variant(self, drop, _pspec):
        variants = ["dark", "light", "glass"]
        self.cfg["theme"]["variant"] = variants[drop.get_selected()]
        self._flush()

    def _on_accent(self, btn):
        rgba = btn.get_rgba()
        self.cfg["theme"]["accent"] = "#{:02x}{:02x}{:02x}".format(
            int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
        )
        # Also update start menu accent
        self.cfg["startmenu"]["accent_color"] = [rgba.red, rgba.green, rgba.blue, rgba.alpha]
        self._flush()

    def _on_glass(self, scale):
        self.cfg["theme"]["glass_intensity"] = scale.get_value()
        self._flush()

    def _on_radius(self, scale):
        self.cfg["theme"]["radius"] = int(scale.get_value())
        self._flush()

    def _on_height(self, scale):
        self.cfg["panel"]["height"] = int(scale.get_value())
        self._flush()

    def _on_margin(self, scale):
        self.cfg["panel"]["margin"] = int(scale.get_value())
        self._flush()

    @staticmethod
    def _parse_hex(hex_str):
        hex_str = hex_str.lstrip("#")
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return Gdk.RGBA(r, g, b, 1.0)
