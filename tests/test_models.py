"""Tests for models.py — SystemSnapshot dataclass."""
from datetime import datetime
from rpi_tempmon.models import SystemSnapshot


def test_snapshot_defaults(normal_snapshot):
    """Alarm defaults to False and hostname is populated."""
    assert normal_snapshot.alarm is False
    assert normal_snapshot.hostname != ""


def test_epoch_property(normal_snapshot):
    """Epoch property returns a positive float."""
    assert isinstance(normal_snapshot.epoch, float)
    assert normal_snapshot.epoch > 0


def test_to_log_text_format(normal_snapshot):
    """Log text contains all expected field labels."""
    text = normal_snapshot.to_log_text()
    assert "TS = " in text
    assert "EP = " in text
    assert "CPU temperature" in text
    assert "GPU temperature" in text
    assert "Cpu usage" in text
    assert "RAM usage" in text
    assert "Swap usage" in text
    assert "Raspberry" in text


def test_to_log_text_alarm(alarm_snapshot):
    """Log text includes Warning line when alarm is True."""
    assert "Warning" in alarm_snapshot.to_log_text()


def test_to_log_text_no_alarm(normal_snapshot):
    """Log text does not include Warning line when alarm is False."""
    assert "Warning" not in normal_snapshot.to_log_text()


def test_snapshot_alarm_flag():
    """Alarm flag can be set explicitly on construction."""
    snap = SystemSnapshot(
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        cpu_temp=75.0,
        gpu_temp=74.0,
        cpu_usage=90.0,
        ram_usage=60.0,
        swap_usage=20.0,
        alarm=True,
    )
    assert snap.alarm is True
