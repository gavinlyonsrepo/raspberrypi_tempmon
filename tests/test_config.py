"""Tests for config.py — loading, validation, and defaults."""
import os
import pytest
from rpi_tempmon.config import load, AppConfig


def _write_cfg(path: str, content: str) -> None:
    """Write content to a config file path, creating dirs as needed."""

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Redirect config and cache dirs to a temp directory for every test."""
    config_dir = tmp_path / ".config" / "rpi_tempmon"
    cache_dir  = tmp_path / ".cache"  / "rpi_tempmon"
    config_dir.mkdir(parents=True)
    cache_dir.mkdir(parents=True)

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("rpi_tempmon.config._HOME",       str(tmp_path))
    monkeypatch.setattr("rpi_tempmon.config.CONFIG_DIR",  str(config_dir))
    monkeypatch.setattr("rpi_tempmon.config.CONFIG_FILE", str(config_dir / "rpi_tempmon.cfg"))
    monkeypatch.setattr("rpi_tempmon.config.CACHE_DIR",   str(cache_dir))

    return config_dir / "rpi_tempmon.cfg"


def test_load_valid_config(isolated_config):
    """Valid config file loads into a correctly typed AppConfig."""
    _write_cfg(str(isolated_config), """
[ALARM]
ALARM_MODE = 1
CPU_UPPERLIMIT = 65

[MAIL]
RPI_AuthUser = test@gmail.com
MAIL_ALERT = 0
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_PASSWORD = secret

[GPIO]
LED_MODE = 0
GPIO_LED = 26
""")
    cfg = load()
    assert isinstance(cfg, AppConfig)
    assert cfg.alarm_mode is True
    assert cfg.cpu_upper_limit == 65
    assert cfg.mail_user == "test@gmail.com"
    assert cfg.smtp.server == "smtp.gmail.com"
    assert cfg.smtp.port == 587
    assert cfg.gpio_led_pin == 26


def test_default_config_created_when_missing(isolated_config):
    """If no config exists a default is created and load() succeeds."""
    assert not isolated_config.exists()
    cfg = load()
    assert isolated_config.exists()
    assert isinstance(cfg, AppConfig)


def test_invalid_cpu_limit(isolated_config):
    """CPU_UPPERLIMIT outside 1-99 raises ValueError."""
    _write_cfg(str(isolated_config), """
[ALARM]
ALARM_MODE = 0
CPU_UPPERLIMIT = 200

[MAIL]
RPI_AuthUser = test@gmail.com
MAIL_ALERT = 0
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_PASSWORD =

[GPIO]
LED_MODE = 0
GPIO_LED = 26
""")
    with pytest.raises(ValueError, match="CPU_UPPERLIMIT must be between"):
        load()


def test_non_integer_cpu_limit(isolated_config):
    """Non-integer CPU_UPPERLIMIT raises ValueError."""
    _write_cfg(str(isolated_config), """
[ALARM]
ALARM_MODE = 0
CPU_UPPERLIMIT = hot

[MAIL]
RPI_AuthUser = test@gmail.com
MAIL_ALERT = 0
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_PASSWORD =

[GPIO]
LED_MODE = 0
GPIO_LED = 26
""")
    with pytest.raises(ValueError, match="CPU_UPPERLIMIT must be an integer"):
        load()


def test_missing_section_raises(isolated_config):
    """Config missing a required section raises ValueError naming that section."""
    _write_cfg(str(isolated_config), """
[ALARM]
ALARM_MODE = 0
CPU_UPPERLIMIT = 70
""")
    with pytest.raises(ValueError, match="missing the \\[MAIL\\] section"):
        load()


def test_invalid_bool_value(isolated_config):
    """Bool field set to value other than 0 or 1 raises ValueError."""
    _write_cfg(str(isolated_config), """
[ALARM]
ALARM_MODE = 2
CPU_UPPERLIMIT = 70

[MAIL]
RPI_AuthUser = test@gmail.com
MAIL_ALERT = 0
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_PASSWORD =

[GPIO]
LED_MODE = 0
GPIO_LED = 26
""")
    with pytest.raises(ValueError, match="must be 0 or 1"):
        load()
