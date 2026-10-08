"""User management: create, edit, delete and list users."""
import sqlite3

from bustransporter import auth

ROLES = ("admin", "engineer")


class UserError(ValueError):
    pass


def _check_role(role):
    if role not in ROLES:
        raise UserError(f"Невалидна роля: {role}")


def create_user(conn, username, password, role):
    _check_role(role)
    if not username or not password:
        raise UserError("Името и паролата са задължителни")
    try:
        cur = conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, auth.hash_password(password), role))
    except sqlite3.IntegrityError:
        raise UserError(f"Потребител {username} вече съществува") from None
    return cur.lastrowid


def update_user(conn, user_id, role=None, password=None):
    get_user(conn, user_id)
    if role is not None:
        _check_role(role)
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    if password is not None:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (auth.hash_password(password), user_id))


def delete_user(conn, user_id):
    get_user(conn, user_id)
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def get_user(conn, user_id):
    row = conn.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise UserError(f"Няма потребител с id {user_id}")
    return dict(row)


def list_users(conn):
    return [dict(r) for r in conn.execute("SELECT id, username, role FROM users ORDER BY username")]
