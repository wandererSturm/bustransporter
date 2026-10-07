import pytest

from bustransporter import db, devices


@pytest.fixture
def conn():
    conn = db.connect()
    conn.execute("INSERT INTO devices (name, ip_address, status) VALUES ('lab-1', '10.0.0.5', 'online')")
    return conn


def test_restart_goes_through_restarting_to_online(conn):
    seen = []

    def controller(ip, command):
        seen.append((ip, command, devices.get_status(conn, 1)))
        return True

    assert devices.restart(conn, 1, controller) is True
    assert seen == [("10.0.0.5", "RESTART", "restarting")]
    assert devices.get_status(conn, 1) == "online"


def test_failed_restart_leaves_device_offline(conn):
    assert devices.restart(conn, 1, lambda ip, command: False) is False
    assert devices.get_status(conn, 1) == "offline"


def test_unknown_device(conn):
    with pytest.raises(devices.DeviceError):
        devices.restart(conn, 42, lambda ip, command: True)
