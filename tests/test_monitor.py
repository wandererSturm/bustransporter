from datetime import datetime

import pytest

from bustransporter import monitor

T = datetime(2026, 10, 7, 14, 30, 5, 123000)


def test_hex_line_has_time_direction_length_and_payload():
    line = monitor.format_packet("in", b"\x01\x2a\x10", T)
    assert line == "14:30:05.123 <- [  3] 01 2A 10"


def test_ascii_line_replaces_non_printable_bytes():
    line = monitor.format_packet("out", b"OK\r\n", T, mode="ascii")
    assert line == "14:30:05.123 -> [  4] OK.."


def test_monitor_can_switch_between_hex_and_ascii():
    m = monitor.Monitor()
    m.add("in", b"Hi", T)
    assert m.render() == ["14:30:05.123 <- [  2] 48 69"]
    m.toggle_mode()
    assert m.render() == ["14:30:05.123 <- [  2] Hi"]


def test_bytes_above_0x7f_from_signed_driver_are_shown_correctly():
    """Regression test for BT-16: 0xFF from a signed driver arrives as -1."""
    assert monitor.format_packet("in", [-1, -128, 127], T) == "14:30:05.123 <- [  3] FF 80 7F"
    assert monitor.format_packet("in", b"\xff\x80", T) == "14:30:05.123 <- [  2] FF 80"


def test_invalid_direction():
    with pytest.raises(ValueError):
        monitor.format_packet("up", b"x", T)
