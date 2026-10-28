"""Vaşak Shell entry point — launches the panel and full-screen start menu.

Command line (used by labwc keybinds):

    vasak-shell              run the panel + start menu daemon
    vasak-shell --toggle     toggle the full-screen start menu
    vasak-shell --show       open the start menu
    vasak-shell --hide       close the start menu
    vasak-shell --quit       stop the running shell
"""

import os
import sys
import signal

# gtk4-layer-shell must be linked before libwayland-client (see its README).
try:
    from ctypes import CDLL
    for _lib in ("libgtk4-layer-shell.so.0", "libgtk4-layer-shell.so"):
        try:
            CDLL(_lib)
            break
        except OSError:
            continue
except Exception:
    pass

from gi.repository import GLib, Gtk, Gdk

# Allow Ctrl+C to quit cleanly
signal.signal(signal.SIGINT, signal.SIG_DFL)

from panel.window import PanelWindow
from startmenu.window import StartMenuWindow

VERSION = "0.1.0"


def load_styles():
    """Load shipped shell.css + user override (~/.config/vasak-shell/user.css)."""
    candidates = [
        "/usr/share/vasak-shell/data/shell.css",
        os.path.join(os.path.dirname(__file__), "..", "data", "shell.css"),
    ]
    for path in candidates:
        if os.path.exists(path):
            provider = Gtk.CssProvider()
            try:
                provider.load_from_path(path)
                display = Gdk.Display.get_default()
                if display is not None:
                    Gtk.StyleContext.add_provider_for_display(
                        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                    )
            except Exception:
                pass
            break

    # User override wins over everything
    user_css = os.path.expanduser("~/.config/vasak-shell/user.css")
    if os.path.exists(user_css):
        provider = Gtk.CssProvider()
        try:
            provider.load_from_path(user_css)
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
                )
        except Exception:
            pass


def _focus_search(startmenu):
    startmenu.search.grab_focus()
    return False


def show_startmenu(startmenu):
    """Show the full-screen start menu and move keyboard focus to search."""
    startmenu.present()
    # present() maps asynchronously; focus once the surface exists.
    GLib.idle_add(_focus_search, startmenu)


def toggle_startmenu(startmenu):
    """Show/hide the full-screen start menu."""
    if startmenu.get_visible():
        startmenu.hide()
    else:
        show_startmenu(startmenu)


def _parse_command(argv):
    """Return (command, error) for the CLI arguments."""
    command = None
    for arg in argv:
        if arg in ("-h", "--help"):
            return "help", None
        if arg in ("-v", "--version"):
            return "version", None
        name = arg[2:] if arg.startswith("--") else None
        if name not in ("toggle", "show", "hide", "quit"):
            return None, "unknown option: %s" % arg
        if command is not None:
            return None, "only one command may be given"
        command = name
    return command, None


def _print_usage(stream=sys.stdout):
    print(
        "usage: vasak-shell [--toggle | --show | --hide | --quit | --version]",
        file=stream,
    )


def run_shell():
    """Run the panel + start menu daemon."""
    Gtk.init()

    from config import ShellConfig
    config = ShellConfig.load()

    load_styles()

    # Top panel (layer-shell)
    panel = PanelWindow(config)

    # Full-screen start menu (hidden by default)
    startmenu = StartMenuWindow(config)
    startmenu.hide()

    loop = GLib.MainLoop()

    def handle(command):
        if command == "toggle":
            toggle_startmenu(startmenu)
        elif command == "show":
            show_startmenu(startmenu)
        elif command == "hide":
            startmenu.hide()
        elif command == "quit":
            loop.quit()

    # App menu button toggles the full-screen start menu
    panel.app_menu_button.connect("clicked", lambda *_: toggle_startmenu(startmenu))

    # Control socket for `vasak-shell --toggle` from labwc keybinds
    from ipc import ShellIPCServer

    server = ShellIPCServer(handle)
    try:
        server.start()
    except OSError as exc:
        print("[vasak-shell] control socket unavailable: %s" % exc, file=sys.stderr)

    signal.signal(signal.SIGTERM, lambda *_: loop.quit())

    panel.present()
    try:
        loop.run()
    finally:
        server.close()

    return 0


def main(argv=None):
    """CLI entry point: send a control command or run the shell."""
    argv = list(sys.argv[1:] if argv is None else argv)
    command, error = _parse_command(argv)

    if error is not None:
        print("vasak-shell: %s" % error, file=sys.stderr)
        _print_usage(sys.stderr)
        return 2

    if command == "help":
        _print_usage()
        return 0

    if command == "version":
        print("vasak-shell %s" % VERSION)
        return 0

    if command is not None:
        from ipc import send_command

        if send_command(command):
            return 0
        print("vasak-shell: no running shell instance", file=sys.stderr)
        return 1

    return run_shell()


if __name__ == "__main__":
    sys.exit(main())
