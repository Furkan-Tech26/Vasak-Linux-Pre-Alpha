"""Vaşak Shell IPC — lightweight message bus between panel and start menu."""

import json
import os
import socket

SOCKET_PATH = "/tmp/vasak-shell.sock"


class ShellIPC:
    """Unix-domain socket IPC for shell components."""

    def __init__(self, path=SOCKET_PATH):
        self.path = path
        self._sock = None

    def connect(self):
        if os.path.exists(self.path):
            os.unlink(self.path)
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self.path)
        self._sock.listen(4)
        return self._sock

    def send(self, message: dict):
        """Send a JSON message to any connected client."""
        data = (json.dumps(message) + "\n").encode("utf-8")
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.path)
            client.sendall(data)
            client.close()
        except (FileNotFoundError, ConnectionRefusedError):
            pass

    def close(self):
        if self._sock:
            self._sock.close()
        if os.path.exists(self.path):
            os.unlink(self.path)
