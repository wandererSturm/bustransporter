"""User management: create, edit, delete and list users.

Every operation takes `actor`, the logged-in user returned by `auth.login()`; only admins are allowed.
"""
import sqlite3

from bustransporter import auth

ROLES = ("admin", "engineer")


class UserError(ValueError):
    pass


class AccessDenied(PermissionError):
    pass


def require_admin(actor):
    if not actor or actor.get("role") != "admin":
        raise AccessDenied("Само администратор има достъп до управлението на потребители")


def _check_role(role):
    if role not in ROLES:
        raise UserError(f"Невалидна роля: {role}")


def create_user(conn, actor, username, password, role):
    require_admin(actor)
    _check_role(role)
    if not username or not password:
        raise UserError("Името и паролата са задължителни")
    try:
        cur = conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, auth.hash_password(password), role))
    except sqlite3.IntegrityError:
        raise UserError(f"Потребител {username} вече съществува") from None
    return cur.lastrowid


def update_user(conn, actor, user_id, role=None, password=None):
    require_admin(actor)
    get_user(conn, user_id)
    if role is not None:
        _check_role(role)
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    if password is not None:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (auth.hash_password(password), user_id))


def delete_user(conn, actor, user_id):
    require_admin(actor)
    if actor.get("id") == user_id:
        raise UserError("Администраторът не може да изтрие себе си")
    get_user(conn, user_id)
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def get_user(conn, user_id):
    row = conn.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise UserError(f"Няма потребител с id {user_id}")
    return dict(row)


def list_users(conn, actor):
    require_admin(actor)
    return [dict(r) for r in conn.execute("SELECT id, username, role FROM users ORDER BY username")]
