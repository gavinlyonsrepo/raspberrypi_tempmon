"""
config.py
Load, validate, and expose the rpi_tempmon configuration file.
Creates a default config file if one is not present.

Config file sections:
    [ALARM]  — temperature threshold settings
    [MAIL]   — email notification settings
    [GPIO]   — LED output settings
"""
import configparser
import os
from dataclasses import dataclass

# Paths follow XDG Base Directory conventions
_HOME = os.environ["HOME"]
CONFIG_DIR = os.path.join(_HOME, ".config", "rpi_tempmon")
CONFIG_FILE = os.path.join(CONFIG_DIR, "rpi_tempmon.cfg")
CACHE_DIR = os.path.join(_HOME, ".cache", "rpi_tempmon")

_DEFAULTS = {
    "ALARM": {
        "ALARM_MODE":     "0",
        "CPU_UPPERLIMIT": "70",
    },
    "MAIL": {
        "RPI_AuthUser":  "example@gmail.com",
        "MAIL_ALERT":    "0",
        "SMTP_SERVER":   "smtp.gmail.com",
        "SMTP_PORT":     "587",
        "SMTP_PASSWORD": "",
    },
    "GPIO": {
        "LED_MODE": "0",
        "GPIO_LED":  "26",
    },
}


@dataclass
class SmtpConfig:
    """SMTP mail settings."""
    server: str
    port: int
    password: str


@dataclass
class AppConfig:
    """Typed, validated representation of rpi_tempmon.cfg."""
    mail_user: str
    mail_alert: bool
    alarm_mode: bool
    cpu_upper_limit: int   # degrees Celsius
    led_mode: bool
    gpio_led_pin: int
    smtp: SmtpConfig


def _ensure_dirs() -> None:
    """Create config and cache directories if they do not exist."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def _write_default_config() -> None:
    """Write a default config file so the user has something to edit."""
    cfg = configparser.ConfigParser()
    cfg.optionxform = lambda option: option   # preserve case
    for section, values in _DEFAULTS.items():
        cfg[section] = values
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        cfg.write(fh)


def _get_section(parser: configparser.ConfigParser, name: str) -> configparser.SectionProxy:
    """Return a config section, raising ValueError if it is missing."""
    try:
        return parser[name]
    except KeyError as exc:
        raise ValueError(
            f"Config file is missing the [{name}] section.\n"
            f"Delete {CONFIG_FILE} and re-run to regenerate a default."
        ) from exc


def load() -> AppConfig:
    """Load and validate the config file. Creates a default if missing.
    Raises ValueError with a human-readable message on bad values."""
    _ensure_dirs()

    if not os.path.isfile(CONFIG_FILE):
        _write_default_config()
        print(f"Config file was missing — created with defaults at:\n  {CONFIG_FILE}")
        print("Edit it to suit your setup, then re-run.\n")

    parser = configparser.ConfigParser()
    parser.optionxform = lambda option: option   # preserve case
    parser.read(CONFIG_FILE)

    alarm = _get_section(parser, "ALARM")
    mail  = _get_section(parser, "MAIL")
    gpio  = _get_section(parser, "GPIO")

    def _bool(section: configparser.SectionProxy, key: str) -> bool:
        val = section.get(key, _DEFAULTS[section.name][key]).strip()
        if val not in ("0", "1"):
            raise ValueError(f"{key} must be 0 or 1, got '{val}'")
        return val == "1"

    # --- ALARM section ---
    try:
        cpu_limit = int(alarm.get("CPU_UPPERLIMIT", _DEFAULTS["ALARM"]["CPU_UPPERLIMIT"]))
    except ValueError as exc:
        raise ValueError("CPU_UPPERLIMIT must be an integer (e.g. 70)") from exc
    if not 1 <= cpu_limit <= 99:
        raise ValueError(f"CPU_UPPERLIMIT must be between 1 and 99, got {cpu_limit}")

    # --- GPIO section ---
    try:
        gpio_pin = int(gpio.get("GPIO_LED", _DEFAULTS["GPIO"]["GPIO_LED"]))
    except ValueError as exc:
        raise ValueError("GPIO_LED must be an integer GPIO pin number (e.g. 26)") from exc

    # --- MAIL section ---
    try:
        smtp_port = int(mail.get("SMTP_PORT", _DEFAULTS["MAIL"]["SMTP_PORT"]))
    except ValueError as exc:
        raise ValueError("SMTP_PORT must be an integer (e.g. 587)") from exc

    return AppConfig(
        mail_user=mail.get("RPI_AuthUser", _DEFAULTS["MAIL"]["RPI_AuthUser"]).strip(),
        mail_alert=_bool(mail, "MAIL_ALERT"),
        alarm_mode=_bool(alarm, "ALARM_MODE"),
        cpu_upper_limit=cpu_limit,
        led_mode=_bool(gpio, "LED_MODE"),
        gpio_led_pin=gpio_pin,
        smtp=SmtpConfig(
            server=mail.get("SMTP_SERVER", _DEFAULTS["MAIL"]["SMTP_SERVER"]).strip(),
            port=smtp_port,
            password=mail.get("SMTP_PASSWORD", _DEFAULTS["MAIL"]["SMTP_PASSWORD"]).strip(),
        ),
    )
