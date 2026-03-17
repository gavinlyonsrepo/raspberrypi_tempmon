"""
sensors.py
Low-level hardware reading functions.
All functions return plain Python floats so callers are not coupled
to subprocess output formats or psutil internals.
"""

import subprocess
import psutil


def get_cpu_temp() -> float:
    """Read ARM CPU temperature from the kernel thermal interface.
    Returns temperature in degrees Celsius."""
    path = "/sys/class/thermal/thermal_zone0/temp"
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    return round(float(raw) / 1000, 1)


def get_gpu_temp() -> float:
    """Read GPU temperature via vcgencmd.
    Returns temperature in degrees Celsius."""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True, text=True, timeout=5, check=True
        )
        # output format: "temp=48.3'C\n"
        raw = result.stdout.strip().replace("temp=", "").replace("'C", "")
        return float(raw)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError) as e:
        raise RuntimeError(f"Could not read GPU temperature: {e}") from e


def get_cpu_usage() -> float:
    """Return current CPU usage as a percentage (0.0 - 100.0)."""
    return psutil.cpu_percent()


def get_ram_usage() -> float:
    """Return current RAM usage as a percentage (0.0 - 100.0)."""
    return psutil.virtual_memory().percent


def get_swap_usage() -> float:
    """Return current swap usage as a percentage (0.0 - 100.0)."""
    return psutil.swap_memory().percent
