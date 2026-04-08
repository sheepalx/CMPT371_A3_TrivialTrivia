from __future__ import annotations

import json
import socket
from typing import Any


def send_json(sock: socket.socket, message: dict[str, Any]) -> None:
    """
    Send exactly one JSON message, framed by a trailing newline.

    TCP is a byte-stream, so we implement application-layer framing using '\n'.
    """
    data = (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
    sock.sendall(data)


def iter_json_messages(sock: socket.socket, *, buffer_size: int = 4096):
    """
    Yield JSON objects from a TCP socket using newline-delimited framing.

    Raises ConnectionError when the peer closes the connection.
    """
    buffer = ""
    while True:
        chunk = sock.recv(buffer_size)
        if not chunk:
            raise ConnectionError("Peer disconnected")
        buffer += chunk.decode("utf-8", errors="replace")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

