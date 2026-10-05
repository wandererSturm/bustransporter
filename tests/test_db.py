import sqlite3

import pytest

from bustransporter import db


def test_all_tables_are_created():
    conn = db.connect()
    tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"users", "devices", "interface_configs", "transfer_sessions", "logs"} <= tables


def test_invalid_role_is_rejected():
    conn = db.connect()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES ('x', 'h', 'guest')")


def test_session_requires_existing_config():
    conn = db.connect()
    conn.execute("INSERT INTO users (username, password_hash, role) VALUES ('eng', 'h', 'engineer')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO transfer_sessions (user_id, config_id, source_ip, target_ip, port) "
                     "VALUES (1, 99, '10.0.0.1', '10.0.0.2', 5000)")
