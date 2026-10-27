"""Vaşak Shell start menu app scanner — discovers .desktop files."""

import os
import configparser

DESKTOP_DIRS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications"),
]


def scan_apps():
    """Return a list of app dicts from .desktop files."""
    apps = []
    seen = set()
    for ddir in DESKTOP_DIRS:
        if not os.path.isdir(ddir):
            continue
        for fname in os.listdir(ddir):
            if not fname.endswith(".desktop"):
                continue
            path = os.path.join(ddir, fname)
            try:
                parser = configparser.ConfigParser()
                parser.read(path)
                entry = parser["Desktop Entry"]
                if entry.get("NoDisplay", "false") == "true":
                    continue
                name = entry.get("Name", fname)
                exec_cmd = entry.get("Exec", "")
                icon = entry.get("Icon", "application-x-executable")
                if name in seen:
                    continue
                seen.add(name)
                apps.append({"name": name, "exec": exec_cmd, "icon": icon})
            except (configparser.Error, OSError):
                continue
    return apps
