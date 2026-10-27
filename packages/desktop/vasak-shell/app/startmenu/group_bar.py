"""Vaşak Shell start menu group bar — named groups like Windows 8.1."""

from gi.repository import Gtk


class GroupBar(Gtk.Box):
    """Horizontal list of clickable group labels that filter the tile grid."""

    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.config = config
        self.set_margin_start(32)
        self.set_margin_end(32)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.add_css_class("group-bar")

        self._buttons = []
        self._grid_filter_cb = None

        # Always offer "All", then configured groups
        names = ["All"] + [g["name"] for g in config.startmenu().get("groups", [])]

        for name in names:
            btn = Gtk.ToggleButton(label=name)
            btn.add_css_class("group-label")
            btn.group_name = name
            btn.connect("toggled", self._on_group_toggled)
            self.append(btn)
            self._buttons.append(btn)

        # "All" active by default
        if self._buttons:
            self._buttons[0].set_active(True)

    def _on_group_toggled(self, button):
        if not button.get_active():
            return

        # Only one group active at a time (skip signal recursion)
        for btn in self._buttons:
            if btn is not button and btn.get_active():
                btn.handler_block_by_func(self._on_group_toggled)
                btn.set_active(False)
                btn.handler_unblock_by_func(self._on_group_toggled)

        # Notify the grid
        if self._grid_filter_cb:
            name = button.group_name
            self._grid_filter_cb(None if name == "All" else name)

    def set_grid_filter_callback(self, cb):
        self._grid_filter_cb = cb
