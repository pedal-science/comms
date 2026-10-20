"""A minimal namchaind client for the video tools: u32 little-endian length prefix and one JSON
body per message (namchain docs/daemon.md, "TCP"). Standard library only."""
import json
import socket
import struct


class Engine:
    def __init__(self, host, port, token):
        self.s = socket.create_connection((host, port))
        hello = self.call({"method": "engine.hello", "protocol": 2, "token": token})
        if not hello.get("ok"):
            raise RuntimeError(f"hello refused: {hello}")

    def _recv(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.s.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("engine closed the connection")
            buf += chunk
        return buf

    def call(self, message):
        body = json.dumps(message).encode()
        self.s.sendall(struct.pack("<I", len(body)) + body)
        (length,) = struct.unpack("<I", self._recv(4))
        return json.loads(self._recv(length))


def from_dev(dev_dir):
    """Connect to a rigpa dev back end (dev/dev-pedal) from its directory."""
    cfg = json.load(open(f"{dev_dir}/namchaind.json"))
    token = open(cfg["tcp_token_file"]).read().strip()
    return Engine(cfg.get("tcp_address", "127.0.0.1"), cfg["tcp_port"], token)


def settle(dev_dir, previous=None, timeout=10.0, still=1.0):
    """Wait until the engine's rig differs from `previous` (a document as JSON text) and has then
    not changed for `still` seconds. Returns the settled document's JSON text."""
    import time
    e = from_dev(dev_dir)
    start = time.monotonic()
    last, since = None, time.monotonic()
    while time.monotonic() - start < timeout:
        doc = json.dumps(e.call({"method": "rig.get"}).get("document"), sort_keys=True)
        if doc != last:
            last, since = doc, time.monotonic()
        elif doc != previous and time.monotonic() - since >= still:
            return doc
        time.sleep(0.15)
    return last


if __name__ == "__main__":
    # engine.py settle <dev dir> <state file> [--save-as <rigs dir>]: wait for the rig to change from
    # what the state file holds and settle, then record it there (and, with --save-as, write it into
    # pedald's library under its own name, so rigpa shows it as a library rig).
    import os
    import sys
    if len(sys.argv) >= 4 and sys.argv[1] == "settle":
        state = sys.argv[3]
        previous = open(state).read() if os.path.exists(state) else None
        doc = settle(sys.argv[2], previous)
        open(state, "w").write(doc or "")
        if "--save-as" in sys.argv and doc:
            rigs = sys.argv[sys.argv.index("--save-as") + 1]
            d = json.loads(doc)
            json.dump(d, open(os.path.join(rigs, f"{d['name']}.json"), "w"), indent=2)
        print("settled" if doc != previous else "unchanged")
    elif len(sys.argv) >= 4 and sys.argv[1] == "load":
        print(from_dev(sys.argv[2]).call({"method": "rig.load", "rig": sys.argv[3]}).get("ok"))
