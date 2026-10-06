import pytest

from bustransporter import auth, db


@pytest.fixture
def conn():
    conn = db.connect()
    conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                 ("ivan", auth.hash_password("secret"), "engineer"))
    return conn


def test_login_returns_user_with_role(conn):
    user = auth.login(conn, "ivan", "secret")
    assert user["username"] == "ivan"
    assert user["role"] == "engineer"


def test_wrong_password_is_rejected(conn):
    with pytest.raises(auth.LoginError):
        auth.login(conn, "ivan", "wrong")


def test_unknown_user_is_rejected(conn):
    with pytest.raises(auth.LoginError):
        auth.login(conn, "nobody", "secret")


def test_password_is_stored_hashed(conn):
    stored = conn.execute("SELECT password_hash FROM users").fetchone()[0]
    assert "secret" not in stored
