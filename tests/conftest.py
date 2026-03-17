"""
conftest.py
Shared pytest fixtures providing mock hardware and config objects
so tests can run on any machine without a Raspberry Pi.
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from rpi_tempmon.config import AppConfig, SmtpConfig
from rpi_tempmon.models import SystemSnapshot


@pytest.fixture
def smtp_cfg():
    """Return a default SmtpConfig for testing."""
    return SmtpConfig(server="smtp.gmail.com", port=587, password="testpass")


@pytest.fixture
def app_cfg(smtp_cfg):
    """Return a default AppConfig for testing."""
    return AppConfig(
        mail_user="test@gmail.com",
        mail_alert=False,
        alarm_mode=True,
        cpu_upper_limit=70,
        led_mode=False,
        gpio_led_pin=26,
        smtp=smtp_cfg,
    )


@pytest.fixture
def normal_snapshot():
    """A snapshot with temperature below the alarm limit."""
    return SystemSnapshot(
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        cpu_temp=55.0,
        gpu_temp=54.5,
        cpu_usage=25.0,
        ram_usage=40.0,
        swap_usage=10.0,
        hostname="raspberrypi",
    )


@pytest.fixture
def alarm_snapshot():
    """A snapshot with temperature above the alarm limit."""
    return SystemSnapshot(
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        cpu_temp=75.0,
        gpu_temp=74.5,
        cpu_usage=90.0,
        ram_usage=60.0,
        swap_usage=20.0,
        hostname="raspberrypi",
        alarm=True,
    )


@pytest.fixture(autouse=True)
def mock_vcgencmd():
    """Prevent real vcgencmd subprocess calls in all tests."""
    with patch("rpi_tempmon.sensors.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="temp=55.0'C\n", returncode=0)
        yield mock_run


@pytest.fixture(autouse=True)
def mock_gpio():
    """Prevent real GPIO operations in all tests."""
    with patch("rpi_tempmon.alarms.LED") as mock_led:
        mock_led.return_value = MagicMock()
        yield mock_led
