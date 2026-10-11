import csv

import pytest

from bustransporter import db, export, users

ADMIN = {"id": 1, "role": "admin"}


@pytest.fixture
def conn():
    conn = db.connect()
    conn.executemany(
        "INSERT INTO logs (session_id, level, event, message, created_at) VALUES (?, 'WARNING', ?, ?, ?)",
        [(None, "info", "started", "2026-10-11 10:00:00"),
         (None, "timeout", "no ACK, 500 ms", "2026-10-11 10:00:05")])
    return conn


def test_csv_has_header_and_rows(conn):
    rows = list(csv.reader(export.logs_to_csv(conn, ADMIN).splitlines()))
    assert rows[0] == ["time", "session", "type", "message"]
    assert rows[2] == ["2026-10-11 10:00:05", "", "timeout", "no ACK, 500 ms"]


def test_export_to_file_keeps_cyrillic(conn, tmp_path):
    conn.execute("INSERT INTO logs (level, event, message) VALUES ('ERROR', 'disconnected', 'Връзката е прекъсната')")
    path = tmp_path / "logs.csv"
    export.export_logs(conn, ADMIN, path)
    assert "Връзката е прекъсната" in path.read_text(encoding="utf-8-sig")


def test_engineer_cannot_export(conn):
    with pytest.raises(users.AccessDenied):
        export.logs_to_csv(conn, {"id": 2, "role": "engineer"})
