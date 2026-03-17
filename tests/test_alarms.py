"""Tests for alarms.py — alarm evaluation and LED control."""
from unittest.mock import MagicMock, patch
from rpi_tempmon import alarms


def test_evaluate_below_limit(normal_snapshot, app_cfg):
    """No alarm when cpu_temp is below the limit."""
    assert alarms.evaluate(normal_snapshot, app_cfg) is False


def test_evaluate_above_limit(alarm_snapshot, app_cfg):
    """Alarm triggers when cpu_temp exceeds the limit."""
    assert alarms.evaluate(alarm_snapshot, app_cfg) is True


def test_evaluate_alarm_mode_off(alarm_snapshot, app_cfg):
    """No alarm when alarm_mode is disabled regardless of temperature."""
    app_cfg.alarm_mode = False
    assert alarms.evaluate(alarm_snapshot, app_cfg) is False


def test_evaluate_at_exact_limit(normal_snapshot, app_cfg):
    """No alarm when cpu_temp equals the limit exactly (must exceed)."""
    normal_snapshot.cpu_temp = 70.0
    assert alarms.evaluate(normal_snapshot, app_cfg) is False


def test_make_led_mode_off(app_cfg):
    """make_led returns None when led_mode is False."""
    app_cfg.led_mode = False
    led = alarms.make_led(app_cfg)
    assert led is None


def test_make_led_mode_on(app_cfg):
    """make_led returns a LED object when led_mode is True."""
    app_cfg.led_mode = True
    mock_led = MagicMock()
    with patch("rpi_tempmon.alarms.LED", return_value=mock_led):
        led = alarms.make_led(app_cfg)
    assert led is mock_led


def test_led_on_calls_on():
    """led_on calls .on() on the LED object."""
    mock_led = MagicMock()
    alarms.led_on(mock_led)
    mock_led.on.assert_called_once()


def test_led_off_calls_off():
    """led_off calls .off() on the LED object."""
    mock_led = MagicMock()
    alarms.led_off(mock_led)
    mock_led.off.assert_called_once()


def test_led_on_none_safe():
    """led_on does not raise when LED is None."""
    alarms.led_on(None)


def test_led_off_none_safe():
    """led_off does not raise when LED is None."""
    alarms.led_off(None)
