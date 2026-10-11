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


def save_profile(conn, device_id, name, bus_type, baud_rate, parity="none"):
    """Store a named configuration so it can be reused later."""
    if not name:
        raise ConfigError("Профилът трябва да има име")
    if conn.execute("SELECT 1 FROM interface_configs WHERE name = ?", (name,)).fetchone():
        raise ConfigError(f"Профил с име {name} вече съществува")
    return save_config(conn, device_id, bus_type, baud_rate, parity, name)


def list_profiles(conn):
    rows = conn.execute("SELECT id, name, bus_type, baud_rate, parity FROM interface_configs "
                        "WHERE name IS NOT NULL ORDER BY name")
    return [dict(r) for r in rows]


def load_profile(conn, name):
    """Return the settings of a saved profile, ready to apply to a bus."""
    row = conn.execute("SELECT bus_type, baud_rate, parity FROM interface_configs WHERE name = ?",
                       (name,)).fetchone()
    if row is None:
        raise ConfigError(f"Няма профил с име {name}")
    return dict(row)
