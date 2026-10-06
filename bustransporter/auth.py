"""Login and password hashing."""
import hashlib
import hmac
import os

ITERATIONS = 100_000


class LoginError(Exception):
    pass


def hash_password(password, salt=None):
    """Return 'salt$hash' using PBKDF2-SHA256; the plain password is never stored."""
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS).hex()
    return f"{salt}${digest}"


def verify_password(password, stored):
    salt, _ = stored.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), stored)


def login(conn, username, password):
    """Return {'id', 'username', 'role'} for valid credentials, otherwise raise LoginError."""
    row = conn.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?",
                       (username,)).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        raise LoginError("Грешно потребителско име или парола")
    return {"id": row["id"], "username": row["username"], "role": row["role"]}
