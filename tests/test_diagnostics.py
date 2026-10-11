import pytest

from bustransporter import bus_config, db, diagnostics, sessions, users

ADMIN = {"id": 1, "role": "admin"}
ENGINEER = {"id": 2, "role": "engineer"}


@pytest.fixture
def conn():
    conn = db.connect()
    users.create_user(conn, ADMIN, "root", "pw", "admin")
    conn.execute("INSERT INTO devices (name, ip_address) VALUES ('lab-1', '10.0.0.5')")
    bus_config.save_config(conn, 1, "UART", 115200)
    sessions.create_session(conn, 1, 1, "10.0.0.5", "192.168.1.20", 5000)
    sessions.create_session(conn, 1, 1, "10.0.0.5", "192.168.1.30", 5000)
    for event, message in [("packet_loss", "lost #12"), ("timeout", "no ACK 500 ms"),
                           ("packet_loss", "lost #40"), ("info", "started")]:
        conn.execute("INSERT INTO logs (session_id, level, event, message) VALUES (1, 'WARNING', ?, ?)",
                     (event, message))
    return conn


def test_session_errors_lists_only_transfer_errors(conn):
    errors = diagnostics.session_errors(conn, ADMIN, 1)
    assert [(e["event"], e["message"]) for e in errors] == [
        ("packet_loss", "lost #12"), ("timeout", "no ACK 500 ms"), ("packet_loss", "lost #40")]


def test_stability_report_counts_errors_per_session(conn):
    first, second = diagnostics.stability_report(conn, ADMIN)
    assert (first["packet_loss"], first["timeout"], first["disconnected"], first["stable"]) == (2, 1, 0, False)
    assert (second["packet_loss"], second["timeout"], second["stable"]) == (0, 0, True)


def test_engineer_has_no_access(conn):
    with pytest.raises(users.AccessDenied):
        diagnostics.stability_report(conn, ENGINEER)
