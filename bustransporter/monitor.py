"""Real-time traffic monitor: formats packets as hex or ascii console lines."""
from datetime import datetime

DIRECTIONS = {"in": "<-", "out": "->"}


def to_hex(data):
    return " ".join(f"{b:02X}" for b in data)


def to_ascii(data):
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def format_packet(direction, data, timestamp=None, mode="hex"):
    """One console line: time, direction, payload in hex or ascii."""
    if direction not in DIRECTIONS:
        raise ValueError(f"Невалидна посока: {direction}")
    if mode not in ("hex", "ascii"):
        raise ValueError(f"Невалиден режим: {mode}")
    timestamp = timestamp or datetime.now()
    payload = to_hex(data) if mode == "hex" else to_ascii(data)
    return f"{timestamp:%H:%M:%S.%f}"[:-3] + f" {DIRECTIONS[direction]} [{len(data):3}] {payload}"


class Monitor:
    """Collects packets and renders them; the display mode can be switched at any time."""

    def __init__(self, mode="hex"):
        self.mode = mode
        self.packets = []

    def add(self, direction, data, timestamp=None):
        self.packets.append((direction, data, timestamp or datetime.now()))

    def toggle_mode(self):
        self.mode = "ascii" if self.mode == "hex" else "hex"

    def render(self):
        return [format_packet(d, data, ts, self.mode) for d, data, ts in self.packets]
