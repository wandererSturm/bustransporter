"""Export of logs to CSV for analysis outside the system."""
import csv
import io

from bustransporter import users

COLUMNS = ("time", "session", "type", "message")


def logs_to_csv(conn, actor, session_id=None):
    """Return the logs as CSV text (columns: time, session, type, message).

    Pass `session_id` to export a single session only.
    """
    users.require_admin(actor)
    query = "SELECT created_at, session_id, event, message FROM logs"
    params = ()
    if session_id is not None:
        query += " WHERE session_id = ?"
        params = (session_id,)
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(COLUMNS)
    writer.writerows(tuple(r) for r in conn.execute(query + " ORDER BY created_at, id", params))
    return out.getvalue()


def export_logs(conn, actor, path, session_id=None):
    """Write the CSV to a file; utf-8-sig so Excel shows Cyrillic correctly."""
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(logs_to_csv(conn, actor, session_id))
