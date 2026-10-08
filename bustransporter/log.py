"""Central logging configuration used by all modules."""
import logging

FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
ROOT = "bustransporter"


def setup(level="INFO", log_file=None):
    """Configure the 'bustransporter' logger: console output and optional file."""
    logger = logging.getLogger(ROOT)
    logger.setLevel(level)
    logger.handlers.clear()
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    for handler in handlers:
        handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(handler)
    return logger


def get_logger(module):
    """Logger for a module, e.g. get_logger('sessions') -> 'bustransporter.sessions'."""
    return logging.getLogger(f"{ROOT}.{module}")


class DbHandler(logging.Handler):
    """Stores log records in the `logs` table so they can be reviewed later.

    Pass `extra={"session_id": ..., "event": ...}` when logging to link a record to a session.
    """

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def emit(self, record):
        self.conn.execute(
            "INSERT INTO logs (session_id, level, event, message) VALUES (?, ?, ?, ?)",
            (getattr(record, "session_id", None), record.levelname,
             getattr(record, "event", "info"), record.getMessage()))
