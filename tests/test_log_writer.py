"""Tests for log_writer.py — file I/O, rotation, CSV, and reporting."""
from rpi_tempmon import log_writer


# ---------------------------------------------------------------------------
# write_log
# ---------------------------------------------------------------------------

def test_write_log_creates_file(tmp_path, normal_snapshot):
    """write_log creates log.txt if it does not exist."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    assert (tmp_path / "log.txt").exists()


def test_write_log_appends(tmp_path, normal_snapshot):
    """write_log appends entries — two calls produce two TS lines."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    log_writer.write_log(normal_snapshot, str(tmp_path))
    content = (tmp_path / "log.txt").read_text(encoding="utf-8")
    assert content.count("TS = ") == 2


def test_write_log_content(tmp_path, normal_snapshot):
    """write_log entry contains CPU and GPU temperature lines."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    content = (tmp_path / "log.txt").read_text(encoding="utf-8")
    assert "CPU temperature" in content
    assert "GPU temperature" in content


# ---------------------------------------------------------------------------
# log rotation
# ---------------------------------------------------------------------------

def test_rotation_triggered(tmp_path):
    """File exceeding max_bytes is renamed to .1."""
    log_path = tmp_path / "log.txt"
    log_path.write_bytes(b"x" * 1_000_001)
    log_writer._rotate_if_needed(str(log_path), max_bytes=1_000_000)  # pylint: disable=protected-access
    assert (tmp_path / "log.txt.1").exists()
    assert not log_path.exists()


def test_rotation_not_triggered_when_small(tmp_path):
    """File under max_bytes is not rotated."""
    log_path = tmp_path / "log.txt"
    log_path.write_text("small content", encoding="utf-8")
    log_writer._rotate_if_needed(str(log_path), max_bytes=1_000_000)  # pylint: disable=protected-access
    assert log_path.exists()
    assert not (tmp_path / "log.txt.1").exists()


def test_rotation_shifts_backups(tmp_path):
    """Existing backups are shifted up by one on rotation."""
    log_path = tmp_path / "log.txt"
    (tmp_path / "log.txt.1").write_text("backup1", encoding="utf-8")
    (tmp_path / "log.txt.2").write_text("backup2", encoding="utf-8")
    log_path.write_bytes(b"x" * 1_000_001)
    log_writer._rotate_if_needed(str(log_path), max_bytes=1_000_000, backup_count=5)  # pylint: disable=protected-access
    assert (tmp_path / "log.txt.2").read_text(encoding="utf-8") == "backup1"
    assert (tmp_path / "log.txt.3").read_text(encoding="utf-8") == "backup2"


# ---------------------------------------------------------------------------
# convert_to_csv
# ---------------------------------------------------------------------------

def test_convert_to_csv(tmp_path, normal_snapshot):
    """CSV file is created from a valid log.txt."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    log_writer.convert_to_csv(str(tmp_path))
    csv_path = tmp_path / "log.csv"
    assert csv_path.exists()
    assert len(csv_path.read_text(encoding="utf-8").strip()) > 0


def test_convert_to_csv_missing_log(tmp_path):
    """convert_to_csv does not raise when log.txt is missing."""
    log_writer.convert_to_csv(str(tmp_path))


# ---------------------------------------------------------------------------
# parse_log and data_report
# ---------------------------------------------------------------------------

def test_parse_log_returns_all_keys(tmp_path, normal_snapshot):
    """parse_log returns a dict containing all expected keys."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    data = log_writer.parse_log(str(tmp_path))
    for key in ("timelist", "cpulist", "gpulist", "cpu_uselist", "ramlist", "swaplist"):
        assert key in data


def test_parse_log_entries_match(tmp_path, normal_snapshot):
    """Two log entries produce two items in timelist."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    log_writer.write_log(normal_snapshot, str(tmp_path))
    data = log_writer.parse_log(str(tmp_path))
    assert len(data["timelist"]) == 2


def test_parse_log_missing_file(tmp_path):
    """parse_log returns empty lists when log.txt does not exist."""
    data = log_writer.parse_log(str(tmp_path))
    assert not data["timelist"]
    assert data["warning_count"] == 0


def test_data_report_no_crash(tmp_path, normal_snapshot):
    """data_report runs without raising on a valid log file."""
    log_writer.write_log(normal_snapshot, str(tmp_path))
    log_writer.data_report(str(tmp_path))
