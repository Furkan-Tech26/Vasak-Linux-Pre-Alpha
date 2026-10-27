"""Vaşak Shell start menu app tile grid — Win 8.1 style."""

from gi.repository import Gtk

from startmenu.tile import AppTile

# Tile width/height hints (in grid columns/rows)
SIZE_HINTS = {
    "small": (1, 1),
    "medium": (1, 1),
    "wide": (2, 1),
    "large": (2, 2),
}


class TileGrid(Gtk.ScrolledWindow):
    """Scrollable grid of live tiles, filterable by group and search text."""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(False)
        self.grid.set_row_spacing(8)
        self.grid.set_column_spacing(8)
        self.grid.set_margin_top(16)
        self.grid.set_margin_bottom(16)
        self.grid.set_margin_start(32)
        self.grid.set_margin_end(32)
        self.set_child(self.grid)

        self._tiles = []
        self._active_group = None
        self._search_text = ""
        self._populate()

    def _group_colors(self):
        """Map group name -> rgba color from config."""
        groups = self.config.startmenu().get("groups", []) or []
        return {g["name"]: g.get("color", [0.39, 0.40, 0.95, 1.0]) for g in groups}

    def _populate(self):
        apps = self.config.apps()
        colors = self._group_colors()
        col = 0
        row = 0
        max_cols = self.config.startmenu().get("columns", 6)

        for app in apps:
            group = app.get("group")
            # Group filter
            if self._active_group and group != self._active_group:
                continue
            # Search filter (case-insensitive)
            if self._search_text and self._search_text.lower() not in app["name"].lower():
                continue

            size = app.get("size", "medium")
            cw, ch = SIZE_HINTS.get(size, (1, 1))

            # Wrap to next row if not enough space
            if col + cw > max_cols:
                col = 0
                row += 1

            tile = AppTile(app, colors.get(group), on_resize=self._rebuild)
            self.grid.attach(tile, col, row, cw, ch)
            self._tiles.append(tile)

            col += cw
            if ch == 2:
                # Large tile occupies two rows; keep column flow
                pass

        # Fill remaining space with empty tiles (Win 8.1 look)
        filler_count = max_cols * 3
        for _ in range(filler_count):
            filler = Gtk.Box()
            filler.set_size_request(88, 88)
            if col >= max_cols:
                col = 0
                row += 1
            self.grid.attach(filler, col, row, 1, 1)
            col += 1

    def _rebuild(self):
        for child in list(self.grid.get_children()):
            self.grid.remove(child)
        self._tiles = []
        self._populate()
        self.grid.queue_resize()

    def set_group_filter(self, group_name):
        """Show only tiles belonging to group_name, or all if None."""
        self._active_group = group_name
        self._rebuild()

    def set_search_filter(self, text):
        """Filter tiles by name substring."""
        self._search_text = text or ""
        self._rebuild()
