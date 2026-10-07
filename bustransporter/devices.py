"""Physical devices and remote restart of their bus interface."""


class DeviceError(Exception):
    pass


def _set_status(conn, device_id, status):
    conn.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_id))


def get_status(conn, device_id):
    row = conn.execute("SELECT status FROM devices WHERE id = ?", (device_id,)).fetchone()
    if row is None:
        raise DeviceError(f"Няма устройство с id {device_id}")
    return row["status"]


def restart(conn, device_id, send_command):
    """Send a restart command to the hardware controller.

    `send_command(ip, command)` talks to the controller and returns True when it is back online.
    Status goes restarting -> online, or offline if the controller does not come back.
    """
    get_status(conn, device_id)
    ip = conn.execute("SELECT ip_address FROM devices WHERE id = ?", (device_id,)).fetchone()[0]
    _set_status(conn, device_id, "restarting")
    ok = send_command(ip, "RESTART")
    _set_status(conn, device_id, "online" if ok else "offline")
    return ok
