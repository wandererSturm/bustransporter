import pytest

from bustransporter import auth, bus_config, db, sessions


@pytest.fixture
def conn():
    conn = db.connect()
    conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'engineer')",
                 ("ivan", auth.hash_password("secret")))
    conn.execute("INSERT INTO devices (name, ip_address) VALUES ('lab-1', '10.0.0.5')")
    bus_config.save_config(conn, 1, "UART", 115200)
    return conn


def test_new_session_is_active(conn):
    session_id = sessions.create_session(conn, 1, 1, "10.0.0.5", "192.168.1.20", 5000)
    session = sessions.get_session(conn, session_id)
    assert session["status"] == "active"
    assert (session["source_ip"], session["target_ip"], session["port"]) == ("10.0.0.5", "192.168.1.20", 5000)


@pytest.mark.parametrize("source, target, port", [
    ("10.0.0.300", "192.168.1.20", 5000),
    ("10.0.0.5", "not-an-ip", 5000),
    ("10.0.0.5", "10.0.0.5", 5000),
    ("10.0.0.5", "192.168.1.20", 70000),
])
def test_invalid_session_is_rejected(conn, source, target, port):
    with pytest.raises(sessions.SessionError):
        sessions.create_session(conn, 1, 1, source, target, port)


def test_session_becomes_disconnected_when_target_is_lost(conn):
    """Regression test for BT-15."""
    session_id = sessions.create_session(conn, 1, 1, "10.0.0.5", "192.168.1.20", 5000)
    assert sessions.check_connection(conn, session_id, lambda ip, port: True) == "active"
    assert sessions.check_connection(conn, session_id, lambda ip, port: False) == "disconnected"
    session = sessions.get_session(conn, session_id)
    assert session["status"] == "disconnected"
    assert session["ended_at"] is not None


def test_closed_session_is_not_reopened_by_heartbeat(conn):
    session_id = sessions.create_session(conn, 1, 1, "10.0.0.5", "192.168.1.20", 5000)
    sessions.close_session(conn, session_id)
    assert sessions.check_connection(conn, session_id, lambda ip, port: False) == "closed"


def test_closed_session(conn):
    session_id = sessions.create_session(conn, 1, 1, "10.0.0.5", "192.168.1.20", 5000)
    sessions.close_session(conn, session_id)
    session = sessions.get_session(conn, session_id)
    assert session["status"] == "closed"
    assert session["ended_at"] is not None
