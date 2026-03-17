"""
log_writer.py
All file I/O: writing log entries, rotating logs, converting log.txt
to CSV, and producing the data analysis report.

The original log.txt format is preserved exactly for backwards
compatibility with existing log files and graph mode.

Log rotation:
    log.txt      — current log
    log.txt.1    — most recent backup
    log.txt.2-5  — older backups
    Default: rotate at 1 MB, keep 5 backups (~14 months at hourly cron)
"""

import csv
import os
from datetime import datetime

from . import display
from .models import SystemSnapshot

# Rotation defaults
_MAX_BYTES    = 1_000_000  # 1 MB
_BACKUP_COUNT = 5


# ---------------------------------------------------------------------------
# Log rotation
# ---------------------------------------------------------------------------

def _rotate_if_needed(log_path: str,
                      max_bytes: int = _MAX_BYTES,
                      backup_count: int = _BACKUP_COUNT) -> None:
    """Rotate log_path if it exceeds max_bytes.

    Shifts existing backups up by one and renames current log to .1.
    Oldest backup beyond backup_count is silently discarded.
    """
    if not os.path.exists(log_path):
        return
    if os.path.getsize(log_path) < max_bytes:
        return

    # Shift existing backups: log.txt.4 -> log.txt.5, etc.
    for i in range(backup_count - 1, 0, -1):
        src = f"{log_path}.{i}"
        dst = f"{log_path}.{i + 1}"
        if os.path.exists(src):
            os.rename(src, dst)

    # Current log becomes .1
    os.rename(log_path, f"{log_path}.1")


# ---------------------------------------------------------------------------
# Writing log entries
# ---------------------------------------------------------------------------

def write_log(snapshot: SystemSnapshot, log_dir: str) -> None:
    """Append one snapshot to log.txt, rotating if the file exceeds 1 MB."""
    log_path = os.path.join(log_dir, "log.txt")
    _rotate_if_needed(log_path)
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(snapshot.to_log_text())
        display.bold("Log entry written.")
    except OSError as exc:
        display.error(f"Could not write log file: {exc}")


def write_log_folder(snapshot: SystemSnapshot, log_dir: str) -> None:
    """Create a timestamped sub-folder and write a single log entry into it."""
    stamp = datetime.now().strftime("%H:%M:%S%a%b%d")
    folder = os.path.join(log_dir, f"{stamp}_RPIT")
    try:
        os.makedirs(folder, exist_ok=True)
        log_path = os.path.join(folder, "log.txt")
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(snapshot.to_log_text())
        display.bold(f"Log folder entry written to {folder}")
    except OSError as exc:
        display.error(f"Could not write log folder entry: {exc}")


# ---------------------------------------------------------------------------
# CSV conversion
# ---------------------------------------------------------------------------

def convert_to_csv(log_dir: str) -> None:
    """Parse log.txt and write log.csv.

    Output columns: timestamp, cpu_temp, gpu_temp, cpu_usage, ram_usage, swap_usage
    Preserves the original positional parsing logic exactly.
    """
    log_path = os.path.join(log_dir, "log.txt")
    csv_path = os.path.join(log_dir, "log.csv")

    if not os.path.isfile(log_path):
        display.error(f"Log file not found at {log_path}")
        return

    try:
        with open(log_path, "r", encoding="utf-8") as log_fh, \
             open(csv_path, "w", newline="", encoding="utf-8") as csv_fh:

            writer = csv.writer(csv_fh)
            time_stamp = cpu_temp = gpu_temp = cpu_use = ram = swap = ""
            # pylint: disable=multiple-statements
            for line in log_fh:
                if "TS"        in line: time_stamp = line[5:-1]
                if "CPU"       in line: cpu_temp   = line[18:22]
                if "GPU"       in line: gpu_temp   = line[18:22]
                if "Cpu"       in line: cpu_use    = line[12:16]
                if "RAM"       in line: ram        = line[12:16]
                if "Swap"      in line: swap       = line[13:17]
                if "Raspberry" in line:
                    writer.writerow([time_stamp, cpu_temp, gpu_temp, cpu_use, ram, swap])
                # pylint: enable=multiple-statements
        display.bold("Log converted to CSV successfully.")
    except (OSError, csv.Error) as exc:
        display.error(f"CSV conversion failed: {exc}")


# ---------------------------------------------------------------------------
# Data analysis / report
# ---------------------------------------------------------------------------

def parse_log(log_dir: str) -> dict:
    """Parse log.txt and return a dict of lists, one list per metric.

    Keys: timelist, unixlist, cpulist, gpulist, cpu_uselist, ramlist,
          swaplist, warning_count.
    Used both by data_report() and by graph mode.
    """
    log_path = os.path.join(log_dir, "log.txt")
    data: dict = {
        "timelist":      [],
        "unixlist":      [],
        "cpulist":       [],
        "gpulist":       [],
        "cpu_uselist":   [],
        "ramlist":       [],
        "swaplist":      [],
        "warning_count": 0,
    }

    if not os.path.isfile(log_path):
        display.error(f"Log file not found at {log_path}")
        return data
    # pylint: disable=multiple-statements
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if "TS"      in line: data["timelist"].append(line[5:-1])
            if "EP"      in line: data["unixlist"].append(line[5:-1])
            if "CPU"     in line: data["cpulist"].append(line[18:20])
            if "GPU"     in line: data["gpulist"].append(line[18:20])
            if "Cpu"     in line: data["cpu_uselist"].append(line[12:16])
            if "RAM"     in line: data["ramlist"].append(line[12:16])
            if "Swap"    in line: data["swaplist"].append(line[13:17])
            if "Warning" in line: data["warning_count"] += 1
    # pylint: enable=multiple-statements

    return data


def data_report(log_dir: str) -> None:
    """Print a summary analysis of the log file to the console."""
    data     = parse_log(log_dir)
    cpulist  = data["cpulist"]
    timelist = data["timelist"]
    cpu_use  = data["cpu_uselist"]
    ramlist  = data["ramlist"]

    if not cpulist:
        display.error("No data found in log file.")
        return

    length = len(cpulist)

    display.bold("\nRaspberry Pi CPU/GPU Temperature Monitor — Data Report")
    print(f"Log file : {os.path.join(log_dir, 'log.txt')}\n")
    print(f"Start : temp {cpulist[0]}'C  at {timelist[0]}")
    print(f"End   : temp {cpulist[-1]}'C  at {timelist[-1]}")
    print(f"Data points : {length}\n")

    try:
        cpu_ints = list(map(int, cpulist))
        print(f"Average temperature : {sum(cpu_ints)/length:.2f}'C")
        print(f"Max temperature     : {max(cpu_ints)}'C")
        print(f"Min temperature     : {min(cpu_ints)}'C")
        print(f"Temperature warnings: {data['warning_count']}\n")

        use_floats = list(map(float, cpu_use))
        print(f"Average CPU usage : {sum(use_floats)/length:.2f}%")
        print(f"Max CPU usage     : {max(use_floats)}%")
        print(f"Min CPU usage     : {min(use_floats)}%\n")

        ram_floats = list(map(float, ramlist))
        print(f"Average RAM usage : {sum(ram_floats)/length:.2f}%")
        print(f"Max RAM usage     : {max(ram_floats)}%")
        print(f"Min RAM usage     : {min(ram_floats)}%")
    except (ValueError, ZeroDivisionError) as exc:
        display.error(f"Could not compute statistics: {exc}")
