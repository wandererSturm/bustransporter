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


def test_save_list_and_load_profiles(conn):
    bus_config.save_profile(conn, 1, "Lab UART", "UART", 115200, "even")
    bus_config.save_profile(conn, 1, "Car CAN", "CAN", 500_000)
    assert [p["name"] for p in bus_config.list_profiles(conn)] == ["Car CAN", "Lab UART"]
    assert bus_config.load_profile(conn, "Lab UART") == {"bus_type": "UART", "baud_rate": 115200, "parity": "even"}


def test_unnamed_configs_are_not_profiles(conn):
    bus_config.save_config(conn, 1, "UART", 9600)
    assert bus_config.list_profiles(conn) == []


def test_profile_name_must_be_unique(conn):
    bus_config.save_profile(conn, 1, "Lab UART", "UART", 115200)
    with pytest.raises(bus_config.ConfigError):
        bus_config.save_profile(conn, 1, "Lab UART", "UART", 9600)


def test_load_missing_profile(conn):
    with pytest.raises(bus_config.ConfigError):
        bus_config.load_profile(conn, "nope")


@pytest.mark.parametrize("bus_type, baud_rate",[("SPI", 9600), ("UART", 12345), ("CAN", 115200)])
def test_invalid_config_is_rejected(conn, bus_type, baud_rate):
    with pytest.raises(bus_config.ConfigError):
        bus_config.save_config(conn, 1, bus_type, baud_rate)
