from __future__ import annotations

import json
import socket
from typing import Any

# transport helper functions for JSON over TCP.
# separating networking logic from server/client code for organization/modularization and to avoid bugs

# send a single JSON message, adding a trailing newline
def send_json(sock: socket.socket, message: dict[str, Any]) -> None:

    data = (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
    sock.sendall(data)


# yield JSON objects from a TCP socket using newline-delimited framing, throws ConnectionError when connection closed
def iter_json_messages(sock: socket.socket, *, buffer_size: int = 4096):
    buf = ""
    # keep reading from the socket until connection closed
    while True:
        chunk = sock.recv(buffer_size)
        if not chunk:
            raise ConnectionError("Peer disconnected")
        buf += chunk.decode("utf-8", errors="replace")
        # keep remainder in buf until the next newline arrives to form a full msg
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

