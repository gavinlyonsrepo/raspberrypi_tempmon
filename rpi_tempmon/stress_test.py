"""stress_test.py — CPU stress test mode using sysbench."""

import csv
import subprocess
import os

from rpi_tempmon import display
from rpi_tempmon import config
from rpi_tempmon import sensors
from rpi_tempmon.graphs import GraphSpec


def run_stress_test(runs: int) -> None:
    """Run the sysbench CPU stress test and optionally graph the results."""
    # Import graph module only when needed (optional dependency)
    try:
        from rpi_tempmon import graphs  # pylint: disable=import-outside-toplevel
    except ImportError:
        display.error("Graph mode requires matplotlib. \
        `Install with: pip install rpi-tempmon[graphs]")
        return

    if not 2 <= runs <= 50:
        display.error("Stress test runs must be between 2 and 50.")
        return

    csv_path = os.path.join(config.CACHE_DIR, "stresslog.csv")
    yaxislist, cpulist, cpu_uselist = [], [], []

    display.bold("RPi tempmon — CPU Stress Test")
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csv_fh:
            writer = csv.writer(csv_fh)
            for i in range(runs):
                cpu_temp = sensors.get_cpu_temp()
                cpu_use  = sensors.get_cpu_usage()
                yaxislist.append(i + 1)
                cpulist.append(str(cpu_temp))
                cpu_uselist.append(str(cpu_use))
                display.bold(f"Run {i+1}: CPU {cpu_temp}'C  usage {cpu_use}%")
                subprocess.run(
                    ["sysbench", "--test=cpu", "--cpu-max-prime=20000",
                     "--num-threads=4", "run"],
                    timeout=120, capture_output=True, check=False,
                )
                writer.writerow([i + 1, cpu_temp, cpu_use])
        print(f"\nResults saved to {csv_path}")
    except FileNotFoundError:
        display.error("sysbench not found. Install with: sudo apt install sysbench")
        return
    except subprocess.TimeoutExpired:
        display.error("sysbench timed out.")
        return

    if input("\nView stress test graph? [y/N] ").lower() == "y":
        graph = graphs.MatplotGraph("RPi Tempmon :")
        graph.draw_graph(
            yaxislist, cpulist, cpu_uselist,
            GraphSpec("CPU temp", "CPU usage (%) / Temperature (°C)",
                      "CPU Temperature and Usage — Stress Test", "CPU usage")
        )
