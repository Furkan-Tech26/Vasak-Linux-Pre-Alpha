"""Shared access to the Vaşak Shell config file (~/.config/vasak-shell/config.json)."""

import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/vasak-shell/config.json")

# Fallback defaults (mirrors vasak-shell config.py)
DEFAULTS = {
    "panel": {
        "position": "top",
        "height": 36,
        "margin": 6,
        "corner_radius": 10,
        "bg_rgba": [0.12, 0.12, 0.14, 0.82],
        "border_color": [0.4, 0.4, 0.5, 0.5],
    },
    "startmenu": {
        "fullscreen": True,
        "bg_rgba": [0.10, 0.10, 0.12, 0.95],
        "accent_color": [0.39, 0.40, 0.95, 1.0],
        "tile_spacing": 8,
        "tile_margin": 12,
        "columns": 6,
        "groups": [
            {"name": "Play", "color": [0.2, 0.6, 1.0, 1.0]},
            {"name": "Explore", "color": [0.2, 0.7, 0.3, 1.0]},
            {"name": "Create", "color": [0.8, 0.4, 0.1, 1.0]},
            {"name": "System", "color": [0.7, 0.2, 0.7, 1.0]},
        ],
    },
    "theme": {
        "variant": "dark",
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


def load():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user = json.load(f)
            return _deep_merge(json.loads(json.dumps(DEFAULTS)), user)
        except (json.JSONDecodeError, OSError):
            pass
    return json.loads(json.dumps(DEFAULTS))


def save(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _deep_merge(base, override):
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result
