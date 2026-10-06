import pytest

from bustransporter import bus_config, db


@pytest.fixture
def conn():
    conn = db.connect()
    conn.execute("INSERT INTO devices (name, ip_address) VALUES ('lab-1', '10.0.0.5')")
    return conn


def test_save_and_read_uart_config(conn):
    config_id = bus_config.save_config(conn, 1, "UART", 115200)
    config = bus_config.get_config(conn, config_id)
    assert (config["bus_type"], config["baud_rate"], config["parity"]) == ("UART", 115200, "none")


def test_can_config_uses_can_baud_rates(conn):
    config_id = bus_config.save_config(conn, 1, "CAN", 500_000)
    assert bus_config.get_config(conn, config_id)["baud_rate"] == 500_000


@pytest.mark.parametrize("bus_type, baud_rate", [("SPI", 9600), ("UART", 12345), ("CAN", 115200)])
def test_invalid_config_is_rejected(conn, bus_type, baud_rate):
    with pytest.raises(bus_config.ConfigError):
        bus_config.save_config(conn, 1, bus_type, baud_rate)
