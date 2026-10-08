import logging

from bustransporter import db, log


def test_setup_writes_to_file(tmp_path):
    log_file = tmp_path / "bt.log"
    log.setup("DEBUG", log_file)
    log.get_logger("sessions").warning("timeout")
    for handler in logging.getLogger(log.ROOT).handlers:
        handler.flush()
    assert "WARNING bustransporter.sessions: timeout" in log_file.read_text(encoding="utf-8")


def test_level_filters_messages(tmp_path):
    log_file = tmp_path / "bt.log"
    log.setup("ERROR", log_file)
    log.get_logger("monitor").info("hidden")
    assert "hidden" not in log_file.read_text(encoding="utf-8")


def test_db_handler_stores_records_with_session_and_event():
    conn = db.connect()
    logger = log.setup("INFO")
    logger.addHandler(log.DbHandler(conn))
    log.get_logger("sessions").error("packet lost", extra={"session_id": None, "event": "packet_loss"})
    row = conn.execute("SELECT level, event, message FROM logs").fetchone()
    assert tuple(row) == ("ERROR", "packet_loss", "packet lost")
