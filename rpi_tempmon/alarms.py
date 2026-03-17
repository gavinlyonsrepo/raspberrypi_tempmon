"""
alarms.py
Alarm evaluation and GPIO LED output.
The LED is initialised once and passed around so gpiozero does not
open the pin repeatedly, which would cause permission errors.
"""

import time
from gpiozero import LED
from gpiozero.exc import GPIOZeroError
from rpi_tempmon import display
from .config import AppConfig
from .models import SystemSnapshot


def evaluate(snapshot: SystemSnapshot, cfg: AppConfig) -> bool:
    """Return True if the snapshot cpu_temp exceeds the configured limit."""
    return cfg.alarm_mode and snapshot.cpu_temp > cfg.cpu_upper_limit


def make_led(cfg: AppConfig):
    """Create and return a gpiozero LED object for the configured pin.
    Returns None (with a warning) if gpiozero is not available or the
    pin cannot be opened (e.g. running on non-Pi hardware)."""
    if not cfg.led_mode:
        return None
    try:
        return LED(cfg.gpio_led_pin)
    except GPIOZeroError as exc:
        display.yellow(f"LED init failed on GPIO {cfg.gpio_led_pin}: {exc}")
        return None


def led_on(led) -> None:
    """Turn the LED on if it was successfully initialised."""
    if led is not None:
        try:
            time.sleep(0.05)
            led.on()
        except GPIOZeroError as exc:
            display.yellow(f"LED on failed: {exc}")


def led_off(led) -> None:
    """Turn the LED off if it was successfully initialised."""
    if led is not None:
        try:
            led.off()
        except GPIOZeroError as exc:
            display.yellow(f"LED off failed: {exc}")


def check_and_signal(snapshot: "SystemSnapshot", cfg: "AppConfig", led) -> None:
    """Evaluate the alarm condition and update the LED + console accordingly."""
    if not cfg.alarm_mode:
        return

    display.bold(f"Alarm mode on — limit: {cfg.cpu_upper_limit}'C")

    if evaluate(snapshot, cfg):
        display.red(f"WARNING: \
            CPU temp {snapshot.cpu_temp}'C exceeds limit {cfg.cpu_upper_limit}'C")
        if cfg.led_mode:
            display.bold(f"LED mode on — GPIO pin: {cfg.gpio_led_pin}")
            led_on(led)
    else:
        led_off(led)
