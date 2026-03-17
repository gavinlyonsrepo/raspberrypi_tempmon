"""Tests for sensors.py — hardware reading with mocked subprocess and files."""
import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from rpi_tempmon import sensors


def test_get_cpu_temp():
    """CPU temp is read from thermal_zone0 and converted from millidegrees."""
    with patch("builtins.open", mock_open(read_data="56200\n")):
        result = sensors.get_cpu_temp()
    assert result == 56.2


def test_get_gpu_temp():
    """GPU temp is parsed from vcgencmd output."""
    mock_result = MagicMock(stdout="temp=55.0'C\n", returncode=0)
    with patch("rpi_tempmon.sensors.subprocess.run", return_value=mock_result):
        result = sensors.get_gpu_temp()
    assert result == 55.0


def test_get_gpu_temp_timeout():
    """TimeoutExpired from vcgencmd raises RuntimeError."""
    with patch("rpi_tempmon.sensors.subprocess.run",
               side_effect=subprocess.TimeoutExpired(cmd="vcgencmd", timeout=5)):
        with pytest.raises(RuntimeError, match="Could not read GPU temperature"):
            sensors.get_gpu_temp()


def test_get_gpu_temp_bad_output():
    """Unparseable vcgencmd output raises RuntimeError."""
    mock_result = MagicMock(stdout="error: not found\n", returncode=0)
    with patch("rpi_tempmon.sensors.subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError):
            sensors.get_gpu_temp()


def test_get_cpu_usage():
    """CPU usage is returned as a float percentage."""
    with patch("rpi_tempmon.sensors.psutil.cpu_percent", return_value=42.5):
        result = sensors.get_cpu_usage()
    assert result == 42.5


def test_get_ram_usage():
    """RAM usage is returned from virtual_memory().percent."""
    mock_mem = MagicMock()
    mock_mem.percent = 55.0
    with patch("rpi_tempmon.sensors.psutil.virtual_memory", return_value=mock_mem):
        result = sensors.get_ram_usage()
    assert result == 55.0


def test_get_swap_usage():
    """Swap usage is returned from swap_memory().percent."""
    mock_swap = MagicMock()
    mock_swap.percent = 12.0
    with patch("rpi_tempmon.sensors.psutil.swap_memory", return_value=mock_swap):
        result = sensors.get_swap_usage()
    assert result == 12.0
