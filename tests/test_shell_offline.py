#!/usr/bin/env python3
"""Offline checks for vasak-shell logic that needs no compositor.

Covers the control socket (command delivery, stale-socket takeover, cleanup)
and the config-colour -> GTK CSS conversion. Both are easy to break and hard
to notice from a screenshot, so CI runs this inside the Arch build container.

Usage: test_shell_offline.py <path to vasak-shell app dir>
"""

import os
import sys
import tempfile
import types

APP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "packages", "desktop", "vasak-shell", "app",
)

# Use the real PyGObject when it is available (the Arch container has it) and
# a minimal stub otherwise, so the socket and colour logic can be checked on a
# machine without GTK installed.
try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk  # noqa: F401
except Exception:
    gi = types.ModuleType("gi")
    repo = types.ModuleType("gi.repository")

    class _GLib:
        @staticmethod
        def idle_add(func, *args):
            func(*args)
            return 0

    class _Gtk:
        STYLE_PROVIDER_PRIORITY_APPLICATION = 600
        STYLE_PROVIDER_PRIORITY_USER = 800

        class CssProvider:
            pass

    class _Gdk:
        class Display:
            @staticmethod
            def get_default():
                return None

    repo.GLib = _GLib
    repo.Gtk = _Gtk
    repo.Gdk = _Gdk
    gi.repository = repo
    sys.modules["gi"] = gi
    sys.modules["gi.repository"] = repo

sys.path.insert(0, APP)

# socket_path() prefers XDG_RUNTIME_DIR; setting it also avoids the getuid()
# fallback, which does not exist on every host.
os.environ["XDG_RUNTIME_DIR"] = tempfile.mkdtemp()

import ipc  # noqa: E402
from cssutil import css_rgba  # noqa: E402

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s %s" % (name, detail))
        failures.append(name)


def main():
    print("css_rgba:")
    check("normalized floats scale to 0..255",
          css_rgba([0.39, 0.40, 0.95, 1.0]) == "rgba(99, 102, 242, 1.0)",
          css_rgba([0.39, 0.40, 0.95, 1.0]))
    check("dark menu background",
          css_rgba([0.10, 0.10, 0.12, 0.95]) == "rgba(26, 26, 31, 0.95)",
          css_rgba([0.10, 0.10, 0.12, 0.95]))
    check("already 0..255 values pass through",
          css_rgba([255, 0, 0, 1]) == "rgba(255, 0, 0, 1.0)",
          css_rgba([255, 0, 0, 1]))
    check("missing alpha defaults to 1",
          css_rgba([1.0, 1.0, 1.0]).endswith(", 1.0)"),
          css_rgba([1.0, 1.0, 1.0]))
    check("None yields opaque white",
          css_rgba(None) == "rgba(255, 255, 255, 1.0)", css_rgba(None))

    print("ipc:")
    # send_command() always dials the module-level SOCKET_PATH, so the server
    # must listen there too.
    sock = ipc.SOCKET_PATH
    seen = []
    server = ipc.ShellIPCServer(seen.append, path=sock)

    try:
        path = server.start()
    except OSError as exc:
        print("  FAIL cannot create control socket: %s" % exc)
        failures.append("socket")
        return finish()

    check("socket created", os.path.exists(path))
    if os.name == "posix":
        check("socket is user-only", oct(os.stat(path).st_mode & 0o777) == "0o600",
              oct(os.stat(path).st_mode & 0o777))

    check("toggle delivered", ipc.send_command("toggle") is True)
    check("show delivered", ipc.send_command("show") is True)
    check("hide delivered", ipc.send_command("hide") is True)
    check("commands reach the handler", seen == ["toggle", "show", "hide"], str(seen))

    try:
        ipc.send_command("bogus")
        check("unknown command rejected", False, "no ValueError")
    except ValueError:
        check("unknown command rejected", True)

    # A restarted shell must take over the socket a crashed shell left behind.
    stale = ipc.ShellIPCServer(lambda cmd: None, path=sock)
    try:
        stale.start()
        check("stale socket replaced", True)
    except OSError as exc:
        check("stale socket replaced", False, str(exc))
    finally:
        stale.close()

    server.close()
    check("socket removed on close", not os.path.exists(path))
    return finish()


def finish():
    if failures:
        print("\n%d FAILED: %s" % (len(failures), failures))
        return 1
    print("\nall offline checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
