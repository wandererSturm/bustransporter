"""Transfer sessions between a source and a target IP address."""
import ipaddress

from bustransporter import log

logger = log.get_logger("sessions")


class SessionError(ValueError):
    pass


def _check_ip(value):
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise SessionError(f"Невалиден IP адрес: {value}") from None


def create_session(conn, user_id, config_id, source_ip, target_ip, port):
    """Open a new TCP/IP transfer session and return its id."""
    _check_ip(source_ip)
    _check_ip(target_ip)
    if source_ip == target_ip:
        raise SessionError("IP източникът и IP целта трябва да са различни")
    if not 1 <= port <= 65535:
        raise SessionError(f"Невалиден порт: {port}")
    cur = conn.execute(
        "INSERT INTO transfer_sessions (user_id, config_id, source_ip, target_ip, port) VALUES (?, ?, ?, ?, ?)",
        (user_id, config_id, source_ip, target_ip, port))
    return cur.lastrowid


def close_session(conn, session_id):
    conn.execute("UPDATE transfer_sessions SET status = 'closed', ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (session_id,))


def check_connection(conn, session_id, is_alive):
    """Heartbeat: mark an active session as disconnected when the target no longer answers.

    `is_alive(target_ip, port)` returns True while the remote side is reachable.
    """
    session = get_session(conn, session_id)
    if session is None or session["status"] != "active":
        return session and session["status"]
    if is_alive(session["target_ip"], session["port"]):
        return "active"
    conn.execute("UPDATE transfer_sessions SET status = 'disconnected', ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (session_id,))
    logger.warning("Връзката към %s:%s е прекъсната", session["target_ip"], session["port"],
                   extra={"session_id": session_id, "event": "disconnected"})
    return "disconnected"


def get_session(conn, session_id):
    row = conn.execute("SELECT * FROM transfer_sessions WHERE id = ?", (session_id,)).fetchone()
    return dict(row) if row else None
