"""Vaşak Shell IPC — single-instance control socket.

The running shell listens on a per-user Unix socket. The command-line
front-end (``vasak-shell --toggle``) connects, sends one JSON command and
exits, which makes the UI controllable from labwc keybinds.

The listener runs in a small daemon thread and dispatches commands onto the
GTK main loop through ``GLib.idle_add`` so GTK is only ever touched from the
main thread.
"""

import json
import os
import socket
import threading


def socket_path():
    """Per-user socket path, preferring the session runtime directory."""
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime and os.path.isdir(runtime):
        return os.path.join(runtime, "vasak-shell.sock")
    return "/tmp/vasak-shell-%d.sock" % os.getuid()


SOCKET_PATH = socket_path()

COMMANDS = ("toggle", "show", "hide", "quit")


def send_command(command, timeout=2.0):
    """Send one command to a running shell.

    Returns True when a shell accepted the command, False otherwise.
    """
    if command not in COMMANDS:
        raise ValueError("unknown command: %s" % command)

    payload = (json.dumps({"command": command}) + "\n").encode("utf-8")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(SOCKET_PATH)
        sock.sendall(payload)
        try:
            reply = sock.recv(64).decode("utf-8", "replace").strip()
        except socket.timeout:
            reply = ""
        return reply in ("", "ok")
    except OSError:
        return False
    finally:
        sock.close()


class ShellIPCServer:
    """Accept control commands and dispatch them on the GTK main loop."""

    def __init__(self, handler, path=None):
        self.path = path or SOCKET_PATH
        self._handler = handler
        self._sock = None
        self._thread = None
        self._running = False

    def start(self):
        """Bind the socket and start the listener thread."""
        if os.path.exists(self.path):
            os.unlink(self.path)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.path)
        os.chmod(self.path, 0o600)
        sock.listen(8)
        sock.settimeout(1.0)
        self._sock = sock
        self._running = True
        self._thread = threading.Thread(
            target=self._serve, name="vasak-shell-ipc", daemon=True
        )
        self._thread.start()
        return self.path

    def _serve(self):
        from gi.repository import GLib

        while self._running:
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            try:
                conn.settimeout(1.0)
                payload = conn.recv(4096)
                handled = False
                for line in payload.decode("utf-8", "replace").splitlines():
                    try:
                        message = json.loads(line)
                    except ValueError:
                        continue
                    command = message.get("command")
                    if command in COMMANDS:
                        # Always run the handler on the GTK main thread.
                        GLib.idle_add(self._dispatch, command)
                        handled = True
                conn.sendall(b"ok\n" if handled else b"error\n")
            except OSError:
                pass
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    def _dispatch(self, command):
        try:
            self._handler(command)
        except Exception as exc:  # never take the shell down from IPC
            print("[vasak-shell] IPC handler failed: %s" % exc)
        return False

    def close(self):
        self._running = False
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        try:
            if os.path.exists(self.path):
                os.unlink(self.path)
        except OSError:
            pass
