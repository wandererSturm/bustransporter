"""Transfer error diagnostics for administrators (packet loss, timeouts, disconnects)."""
from bustransporter import users

ERROR_EVENTS = ("packet_loss", "timeout", "disconnected")


def session_errors(conn, actor, session_id):
    """All transfer errors of one session, oldest first."""
    users.require_admin(actor)
    placeholders = ", ".join("?" * len(ERROR_EVENTS))
    rows = conn.execute(
        f"SELECT created_at, event, message FROM logs WHERE session_id = ? AND event IN ({placeholders}) "
        "ORDER BY created_at, id", (session_id, *ERROR_EVENTS))
    return [dict(r) for r in rows]


def stability_report(conn, actor):
    """Per session: number of packet losses, timeouts and disconnects."""
    users.require_admin(actor)
    rows = conn.execute(
        "SELECT s.id AS session_id, s.source_ip, s.target_ip, s.status, "
        "       SUM(l.event = 'packet_loss')  AS packet_loss, "
        "       SUM(l.event = 'timeout')      AS timeout, "
        "       SUM(l.event = 'disconnected') AS disconnected "
        "FROM transfer_sessions s LEFT JOIN logs l ON l.session_id = s.id "
        "GROUP BY s.id ORDER BY s.id")
    report = []
    for r in rows:
        row = dict(r)
        for event in ERROR_EVENTS:
            row[event] = row[event] or 0
        row["stable"] = sum(row[e] for e in ERROR_EVENTS) == 0
        report.append(row)
    return report
