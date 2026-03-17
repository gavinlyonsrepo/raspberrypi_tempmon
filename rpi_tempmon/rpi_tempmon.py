#!/usr/bin/env python3
"""
rpi_tempmon.py — Raspberry Pi system temperature monitor.

URL: https://github.com/gavinlyonsrepo/raspberrypi_tempmon
"""
import argparse
import datetime
import os
import signal
import sys
import time

from rpi_tempmon import display
from rpi_tempmon import sensors
from rpi_tempmon import alarms
from rpi_tempmon import notifiers
from rpi_tempmon import log_writer
from rpi_tempmon import stress_test
from rpi_tempmon.config import load as load_config, CACHE_DIR
from rpi_tempmon.models import SystemSnapshot

__VERSION__ = "3.1.1"
__URL__ = "https://github.com/gavinlyonsrepo/raspberrypi_tempmon"

# ---------------------------------------------------------------------------
# Signal handling — ensures the GPIO LED is always turned off on exit
# _state dict is a mutable container so the signal handler can access the
# LED without needing a global statement in each mode function.
# ---------------------------------------------------------------------------
_state = {"led": None}


def _shutdown(*_):
    alarms.led_off(_state["led"])
    display.bold(f"\nGoodbye {os.environ.get('USER', '')}")
    sys.exit(0)


signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


# ---------------------------------------------------------------------------
# Snapshot helper
# ---------------------------------------------------------------------------

def take_snapshot(cfg) -> SystemSnapshot:
    """Read all sensors and return a SystemSnapshot."""
    now = datetime.datetime.now()
    cpu_temp  = float(sensors.get_cpu_temp())
    gpu_temp  = sensors.get_gpu_temp()
    cpu_usage = float(sensors.get_cpu_usage())
    ram_usage = float(sensors.get_ram_usage())
    swap_usage = float(sensors.get_swap_usage())

    snap = SystemSnapshot(
        timestamp=now,
        cpu_temp=cpu_temp,
        gpu_temp=gpu_temp,
        cpu_usage=cpu_usage,
        ram_usage=ram_usage,
        swap_usage=swap_usage,
    )
    snap.alarm = alarms.evaluate(snap, cfg)
    return snap


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_snapshot(snap: SystemSnapshot) -> None:
    """Print one snapshot to the terminal."""
    os.system("clear")
    print()
    display.line()
    display.bold("Raspberry Pi CPU/GPU Temperature Monitor")
    print(snap.timestamp.strftime("%y-%m-%d %H:%M:%S"))
    print(snap.hostname)
    display.line()
    printer = display.red if snap.alarm else display.green
    printer(f"CPU temp  => {snap.cpu_temp}'C")
    printer(f"GPU temp  => {snap.gpu_temp}'C")
    display.green(f"CPU usage => {snap.cpu_usage}%")
    display.green(f"RAM usage => {snap.ram_usage}%")
    display.green(f"Swap usage => {snap.swap_usage}%\n")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser(
        description=f"Raspberry Pi temperature monitor — {__URL__}"
    )
    parser.add_argument("-v", dest="version",     action="store_true", help="Print version and exit")
    parser.add_argument("-l", dest="logfile",     action="store_true", help="Log to file")
    parser.add_argument("-L", dest="logfolder",   action="store_true", help="Log to timestamped folder")
    parser.add_argument("-m", dest="mail",        action="store_true", help="Send log by email")
    parser.add_argument("-s", dest="csv_convert", action="store_true", help="Convert log.txt to log.csv")
    parser.add_argument("-a", dest="data",        action="store_true", help="Analyse log file and report")
    parser.add_argument("-g", dest="graphlog",    action="store_true", help="Graph mode (requires [graphs] extra)")
    parser.add_argument("-c", dest="cont",        type=int, metavar="SECS", help="Continuous mode, delay in seconds")
    parser.add_argument("-n", dest="notify",      type=int, metavar="MODE", help="Desktop notify: 2=always, 3=alarm only")
    parser.add_argument("-ST", dest="stresstest", type=int, metavar="RUNS", help="Stress test, number of runs (2-50)")
    # pylint: enable=line-too-long
    return parser


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------

def run_normal_mode(cfg):
    """Normal single-shot mode: display once, prompt to repeat."""
    _state["led"] = alarms.make_led(cfg)
    scan_count = 0

    while True:
        snap = take_snapshot(cfg)
        scan_count += 1
        print_snapshot(snap)
        display.bold(f"Scans: {scan_count}")
        alarms.check_and_signal(snap, cfg, _state["led"])
        if not display.yesno("Repeat?"):
            break

    alarms.led_off(_state["led"])
    display.bold(f"\nGoodbye {os.environ.get('USER', '')}")


def run_continuous_mode(cfg, delay: int):
    """Continuous mode: display and repeat on a timer."""
    _state["led"] = alarms.make_led(cfg)
    scan_count = 0

    while True:
        snap = take_snapshot(cfg)
        scan_count += 1
        print_snapshot(snap)
        display.bold(f"Scans: {scan_count}")
        display.bold(f"Continuous mode — interval: {delay}s. Press CTRL+C to quit.")
        alarms.check_and_signal(snap, cfg, _state["led"])
        time.sleep(float(delay))


def run_logfile_mode(cfg):
    """Write one snapshot to log.txt, optionally email on alarm."""
    snap = take_snapshot(cfg)
    log_writer.write_log(snap, CACHE_DIR)
    if cfg.mail_alert and snap.alarm:
        notifiers.send_mail(" Warning ", cfg)


def run_logfolder_mode(cfg):
    """Write one snapshot to a new timestamped sub-folder."""
    snap = take_snapshot(cfg)
    log_writer.write_log_folder(snap, CACHE_DIR)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _route(args, cfg) -> None:
    """Dispatch to the correct mode based on parsed CLI arguments."""
    if args.csv_convert:
        log_writer.convert_to_csv(CACHE_DIR)
    elif args.logfolder:
        run_logfolder_mode(cfg)
    elif args.data:
        log_writer.data_report(CACHE_DIR)
    elif args.logfile:
        run_logfile_mode(cfg)
    elif args.notify is not None:
        snap = take_snapshot(cfg)
        notifiers.notify(str(args.notify), snap.cpu_temp, cfg.cpu_upper_limit)
    elif args.mail:
        if cfg.mail_alert:
            notifiers.send_mail(" Mail mode ", cfg)
        else:
            display.yellow("Mail alert is disabled in config (MAIL_ALERT = 0).")
    elif args.graphlog:
        _run_graph_mode(cfg)
    elif args.stresstest is not None:
        stress_test.run_stress_test(args.stresstest)
    elif args.cont is not None:
        run_continuous_mode(cfg, args.cont)
    else:
        run_normal_mode(cfg)


def _run_graph_mode(_) -> None:
    """Load matplotlib and launch graph mode."""
    try:
        from rpi_tempmon import graphs  # pylint: disable=import-outside-toplevel
    except ImportError:
        display.error("Graph mode requires matplotlib. \
            Install with: pip install rpi-tempmon[graphs]")
        sys.exit(1)
    graph = graphs.MatplotGraph("RPi Tempmon :")
    graph.graph_log_data(CACHE_DIR)


def main() -> None:
    """Entry point: parse arguments, load config, and dispatch to the correct mode."""
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        display.bold(f"rpi-tempmon version {__VERSION__}")
        sys.exit(0)

    try:
        cfg = load_config()
    except ValueError as exc:
        display.error(str(exc))
        sys.exit(1)

    _route(args, cfg)


if __name__ == "__main__":
    main()
