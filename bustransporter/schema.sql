-- Bus Transporter database schema (see ERD in the client specification)

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin', 'engineer'))
);

CREATE TABLE IF NOT EXISTS devices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    ip_address  TEXT NOT NULL,
    mac_address TEXT,
    status      TEXT NOT NULL DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'restarting'))
);

CREATE TABLE IF NOT EXISTS interface_configs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id  INTEGER NOT NULL REFERENCES devices (id),
    name       TEXT,
    bus_type   TEXT    NOT NULL CHECK (bus_type IN ('CAN', 'UART', 'USB')),
    baud_rate  INTEGER NOT NULL,
    parity     TEXT    NOT NULL DEFAULT 'none'
);

CREATE TABLE IF NOT EXISTS transfer_sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users (id),
    config_id  INTEGER NOT NULL REFERENCES interface_configs (id),
    source_ip  TEXT    NOT NULL,
    target_ip  TEXT    NOT NULL,
    port       INTEGER NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'disconnected', 'closed')),
    started_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at   TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES transfer_sessions (id),
    level      TEXT NOT NULL,
    event      TEXT NOT NULL,
    message    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
