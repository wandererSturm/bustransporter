"""Bus interface configuration (type and baud rate)."""

BUS_TYPES = ("CAN", "UART")
BAUD_RATES = {
    "UART": (9600, 19200, 38400, 57600, 115200),
    "CAN": (125_000, 250_000, 500_000, 1_000_000),
}
PARITIES = ("none", "even", "odd")


class ConfigError(ValueError):
    pass


def validate(bus_type, baud_rate, parity="none"):
    if bus_type not in BUS_TYPES:
        raise ConfigError(f"Неподдържан тип интерфейс: {bus_type}")
    if baud_rate not in BAUD_RATES[bus_type]:
        raise ConfigError(f"Невалиден baud rate {baud_rate} за {bus_type}")
    if parity not in PARITIES:
        raise ConfigError(f"Невалиден parity: {parity}")


def save_config(conn, device_id, bus_type, baud_rate, parity="none", name=None):
    """Validate and store a configuration; return its id."""
    validate(bus_type, baud_rate, parity)
    cur = conn.execute(
        "INSERT INTO interface_configs (device_id, name, bus_type, baud_rate, parity) VALUES (?, ?, ?, ?, ?)",
        (device_id, name, bus_type, baud_rate, parity))
    return cur.lastrowid


def get_config(conn, config_id):
    row = conn.execute("SELECT * FROM interface_configs WHERE id = ?", (config_id,)).fetchone()
    return dict(row) if row else None
