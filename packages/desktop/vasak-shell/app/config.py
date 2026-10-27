"""Vaşak Shell configuration — panel, start menu, tiles, themes."""

import os
import json

DEFAULT_CONFIG = {
    "panel": {
        "position": "top",
        "height": 36,
        "margin": 6,
        "corner_radius": 10,
        "bg_rgba": [0.12, 0.12, 0.14, 0.82],
        "border_color": [0.4, 0.4, 0.5, 0.5],
    },
    "startmenu": {
        # Windows 8.1 style: full-screen overlay
        "fullscreen": True,
        "bg_rgba": [0.10, 0.10, 0.12, 0.95],
        "accent_color": [0.39, 0.40, 0.95, 1.0],   # Vaşak blue/purple
        "tile_spacing": 8,
        "tile_margin": 12,
        "columns": 6,           # tile grid columns
        "groups": [             # named tile groups like Win 8.1
            {"name": "Play", "color": [0.2, 0.6, 1.0, 1.0]},
            {"name": "Explore", "color": [0.2, 0.7, 0.3, 1.0]},
            {"name": "Create", "color": [0.8, 0.4, 0.1, 1.0]},
            {"name": "System", "color": [0.7, 0.2, 0.7, 1.0]},
        ],
    },
    "theme": {
        "variant": "dark",      # dark | light | glass
        "accent": "#6366f1",
        "glass_intensity": 0.82,
        "radius": 12,
    },
    "apps": [
        {"name": "Terminal", "exec": "foot", "icon": "utilities-terminal", "group": "System", "size": "medium", "live": False},
        {"name": "File Manager", "exec": "thunar", "icon": "system-file-manager", "group": "Explore", "size": "medium", "live": False},
        {"name": "Web Browser", "exec": "firefox", "icon": "web-browser", "group": "Explore", "size": "wide", "live": True},
        {"name": "Settings", "exec": "vasak-settings", "icon": "vasak-settings", "group": "System", "size": "medium", "live": False},
        {"name": "Text Editor", "exec": "mousepad", "icon": "accessories-text-editor", "group": "Create", "size": "medium", "live": False},
    ],
}

CONFIG_PATH = os.path.expanduser("~/.config/vasak-shell/config.json")


class ShellConfig:
    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                data = json.loads(json.dumps(DEFAULT_CONFIG))
                data = cls._deep_merge(data, user_cfg)
                return cls(data)
            except (json.JSONDecodeError, OSError):
                pass
        return cls(DEFAULT_CONFIG)

    @staticmethod
    def _deep_merge(default, override):
        result = dict(default)
        for key, val in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = ShellConfig._deep_merge(result[key], val)
            else:
                result[key] = val
        return result

    def save(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def panel(self):
        return self.data["panel"]

    def startmenu(self):
        return self.data["startmenu"]

    def theme(self):
        return self.data["theme"]

    def apps(self):
        return self.data["apps"]
