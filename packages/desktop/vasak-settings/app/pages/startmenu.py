"""Start Menu page — Win 8.1 tile layout, groups, and app editor (fully customizable)."""

from gi.repository import Gtk, Adw, Gdk

import shellconfig

SIZES = ["small", "medium", "wide", "large"]


class StartMenuPage(Adw.NavigationPage):
    def __init__(self):
        super().__init__()
        self.cfg = shellconfig.load()

        page = Adw.PreferencesPage()
        self.set_child(page)

        # ============ Layout ============
        layout = Adw.PreferencesGroup()
        layout.set_title("Layout")
        layout.set_description("Windows 8.1 style full-screen tile menu")
        page.add(layout)

        fs_row = Adw.ActionRow()
        fs_row.set_title("Full-screen start menu")
        fs_row.set_subtitle("On = Win 8.1 style overlay, Off = compact popup")
        self.fs_switch = Gtk.Switch()
        self.fs_switch.set_active(self.cfg["startmenu"].get("fullscreen", True))
        self.fs_switch.connect("notify::active", self._on_fullscreen)
        fs_row.add_suffix(self.fs_switch)
        layout.add(fs_row)

        cols_row = Adw.ActionRow()
        cols_row.set_title("Tile columns")
        self.cols_spin = Gtk.SpinButton.new_with_range(3, 12, 1)
        self.cols_spin.set_value(self.cfg["startmenu"].get("columns", 6))
        self.cols_spin.connect("value-changed", self._on_columns)
        cols_row.add_suffix(self.cols_spin)
        layout.add(cols_row)

        spacing_row = Adw.ActionRow()
        spacing_row.set_title("Tile spacing")
        self.spacing_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 24, 1)
        self.spacing_scale.set_value(self.cfg["startmenu"].get("tile_spacing", 8))
        self.spacing_scale.set_hexpand(True)
        self.spacing_scale.connect("value-changed", self._on_spacing)
        spacing_row.add_suffix(self.spacing_scale)
        layout.add(spacing_row)

        # ============ Groups ============
        groups = Adw.PreferencesGroup()
        groups.set_title("Groups")
        groups.set_description("Named tile groups with their own color")
        page.add(groups)

        for group in self.cfg["startmenu"].get("groups", []):
            groups.add(self._make_group_row(group, groups))

        add_group_row = Adw.ActionRow()
        add_group_row.set_title("Add group")
        self.new_group_entry = Gtk.Entry()
        self.new_group_entry.set_placeholder_text("Group name")
        self.new_group_entry.set_width_chars(14)
        add_group_row.add_suffix(self.new_group_entry)
        add_btn = Gtk.Button.new_from_icon_name("list-add-symbolic")
        add_btn.add_css_class("flat")
        add_btn.connect("clicked", lambda *_: self._add_group(groups))
        add_group_row.add_suffix(add_btn)
        groups.add(add_group_row)

        # ============ App tiles ============
        apps_group = Adw.PreferencesGroup()
        apps_group.set_title("App tiles")
        apps_group.set_description("Choose size, group and live content for each tile")
        page.add(apps_group)

        self._apps_group = apps_group
        for app in self.cfg["apps"]:
            apps_group.add(self._make_app_row(app))

        # ============ Add app ============
        add_app_group = Adw.PreferencesGroup()
        add_app_group.set_title("Add an app tile")
        page.add(add_app_group)

        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text("Name (e.g. Spotify)")
        self.exec_entry = Gtk.Entry()
        self.exec_entry.set_placeholder_text("Exec (e.g. spotify)")
        self.icon_entry = Gtk.Entry()
        self.icon_entry.set_placeholder_text("Icon (e.g. spotify)")

        for entry, title in (
            (self.name_entry, "Name"),
            (self.exec_entry, "Exec"),
            (self.icon_entry, "Icon"),
        ):
            row = Adw.ActionRow()
            row.set_title(title)
            row.add_suffix(entry)
            add_app_group.add(row)

        group_names = [g["name"] for g in self.cfg["startmenu"].get("groups", [])]
        combo_row = Adw.ActionRow()
        combo_row.set_title("Group")
        self.new_app_group = Gtk.DropDown.new_from_strings(group_names or ["Default"])
        combo_row.add_suffix(self.new_app_group)
        add_app_group.add(combo_row)

        size_row = Adw.ActionRow()
        size_row.set_title("Size")
        self.new_app_size = Gtk.DropDown.new_from_strings(SIZES)
        size_row.add_suffix(self.new_app_size)
        add_app_group.add(size_row)

        live_row = Adw.ActionRow()
        live_row.set_title("Live tile")
        self.new_app_live = Gtk.Switch()
        live_row.add_suffix(self.new_app_live)
        add_app_group.add(live_row)

        add_app_btn_row = Adw.ActionRow()
        add_app_btn = Gtk.Button(label="Add app tile")
        add_app_btn.add_css_class("suggested-action")
        add_app_btn.connect("clicked", self._add_app)
        add_app_btn_row.add_suffix(add_app_btn)
        add_app_group.add(add_app_btn_row)

        # Save hint
        hint = Adw.ActionRow()
        hint.set_title("Changes save automatically")
        hint.set_subtitle("Restart vasak-shell to apply (or log out/in)")
        page.add(hint)

    # ============ Group rows ============

    def _make_group_row(self, group, parent_group):
        row = Adw.ActionRow()
        row.set_title(group["name"])

        color_btn = Gtk.ColorButton.new()
        rgba = group.get("color", [0.4, 0.4, 0.9, 1.0])
        color_btn.set_rgba(Gdk.RGBA(rgba[0], rgba[1], rgba[2], rgba[3]))
        color_btn.connect("color-set", lambda btn: self._on_group_color(group, btn))
        row.add_suffix(color_btn)

        del_btn = Gtk.Button.new_from_icon_name("edit-delete-symbolic")
        del_btn.add_css_class("flat")
        del_btn.set_tooltip_text(f"Delete group {group['name']}")
        del_btn.connect("clicked", lambda *_: self._delete_group(group, row, parent_group))
        row.add_suffix(del_btn)
        return row

    def _on_group_color(self, group, btn):
        rgba = btn.get_rgba()
        group["color"] = [rgba.red, rgba.green, rgba.blue, rgba.alpha]
        shellconfig.save(self.cfg)

    def _add_group(self, parent_group):
        name = self.new_group_entry.get_text().strip()
        if not name:
            return
        group = {"name": name, "color": [0.4, 0.4, 0.9, 1.0]}
        self.cfg["startmenu"].setdefault("groups", []).append(group)
        shellconfig.save(self.cfg)
        parent_group.add(self._make_group_row(group, parent_group))
        self.new_group_entry.set_text("")

    def _delete_group(self, group, row, parent_group):
        self.cfg["startmenu"]["groups"] = [
            g for g in self.cfg["startmenu"].get("groups", []) if g["name"] != group["name"]
        ]
        shellconfig.save(self.cfg)
        parent_group.remove(row)

    # ============ App rows ============

    def _make_app_row(self, app):
        row = Adw.ExpanderRow()
        row.set_title(app["name"])
        row.set_subtitle(f"{app.get('size', 'medium')} tile")

        # Size dropdown
        size_row = Adw.ActionRow()
        size_row.set_title("Size")
        size_drop = Gtk.DropDown.new_from_strings(SIZES)
        if app.get("size") in SIZES:
            size_drop.set_selected(SIZES.index(app["size"]))
        size_drop.connect("notify::selected", lambda d, _p: self._on_app_size(app, d, row))
        size_row.add_suffix(size_drop)
        row.add_row(size_row)

        # Group dropdown
        group_names = [g["name"] for g in self.cfg["startmenu"].get("groups", [])]
        group_row = Adw.ActionRow()
        group_row.set_title("Group")
        group_drop = Gtk.DropDown.new_from_strings(group_names or ["Default"])
        if app.get("group") in group_names:
            group_drop.set_selected(group_names.index(app["group"]))
        group_drop.connect("notify::selected", lambda d, _p: self._on_app_group(app, d, group_names))
        group_row.add_suffix(group_drop)
        row.add_row(group_row)

        # Live toggle
        live_row = Adw.ActionRow()
        live_row.set_title("Live tile")
        live_switch = Gtk.Switch()
        live_switch.set_active(bool(app.get("live", False)))
        live_switch.connect("notify::active", lambda s, _p: self._on_app_live(app, s))
        live_row.add_suffix(live_switch)
        row.add_row(live_row)

        # Remove button
        del_btn = Gtk.Button.new_from_icon_name("edit-delete-symbolic")
        del_btn.add_css_class("flat")
        del_btn.connect("clicked", lambda *_: self._delete_app(app, row))
        row.add_suffix(del_btn)

        return row

    def _on_app_size(self, app, drop, row):
        app["size"] = SIZES[drop.get_selected()]
        row.set_subtitle(f"{app['size']} tile")
        shellconfig.save(self.cfg)

    def _on_app_group(self, app, drop, group_names):
        if group_names:
            app["group"] = group_names[drop.get_selected()]
        shellconfig.save(self.cfg)

    def _on_app_live(self, app, switch):
        app["live"] = switch.get_active()
        shellconfig.save(self.cfg)

    def _delete_app(self, app, row):
        self.cfg["apps"] = [a for a in self.cfg["apps"] if a is not app]
        shellconfig.save(self.cfg)
        self._apps_group.remove(row)

    # ============ Layout callbacks ============

    def _on_fullscreen(self, switch, _pspec):
        self.cfg["startmenu"]["fullscreen"] = switch.get_active()
        shellconfig.save(self.cfg)

    def _on_columns(self, spin):
        self.cfg["startmenu"]["columns"] = int(spin.get_value())
        shellconfig.save(self.cfg)

    def _on_spacing(self, scale):
        self.cfg["startmenu"]["tile_spacing"] = int(scale.get_value())
        shellconfig.save(self.cfg)

    # ============ Add app ============

    def _add_app(self):
        name = self.name_entry.get_text().strip()
        exec_cmd = self.exec_entry.get_text().strip()
        if not name or not exec_cmd:
            return
        group_names = [g["name"] for g in self.cfg["startmenu"].get("groups", [])]
        group = group_names[self.new_app_group.get_selected()] if group_names else "Default"
        app = {
            "name": name,
            "exec": exec_cmd,
            "icon": self.icon_entry.get_text().strip() or "application-x-executable",
            "group": group,
            "size": SIZES[self.new_app_size.get_selected()],
            "live": self.new_app_live.get_active(),
        }
        self.cfg["apps"].append(app)
        shellconfig.save(self.cfg)
        self._apps_group.add(self._make_app_row(app))

        self.name_entry.set_text("")
        self.exec_entry.set_text("")
        self.icon_entry.set_text("")
        self.new_app_live.set_active(False)
