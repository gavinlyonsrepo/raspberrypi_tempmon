"""
models.py
Data model for a single system monitoring snapshot.
"""
import socket
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SystemSnapshot: # pylint: disable=too-many-instance-attributes
    """Represents one point-in-time reading of all monitored system metrics."""
    timestamp: datetime
    cpu_temp: float        # degrees Celsius
    gpu_temp: float        # degrees Celsius
    cpu_usage: float       # percent 0-100
    ram_usage: float       # percent 0-100
    swap_usage: float      # percent 0-100
    hostname: str = field(default_factory=socket.gethostname)
    alarm: bool = False    # True if cpu_temp exceeded the configured limit

    @property
    def epoch(self) -> float:
        """Unix epoch timestamp, used by graph modes 5-8."""
        return self.timestamp.timestamp()

    def to_log_text(self) -> str:
        """Render in the original log.txt format for backwards compatibility."""
        lines = [
            f"TS = {self.timestamp.strftime('%y-%m-%d %H:%M:%S')}",
            f"EP = {round(self.epoch, 0)}",
            f"GPU temperature = {self.gpu_temp}'C",
            f"CPU temperature = {self.cpu_temp}",
            f"Cpu usage = {self.cpu_usage}",
            f"RAM usage = {self.ram_usage}",
            f"Swap usage = {self.swap_usage}",
            f"Raspberry pi temperature monitor: {self.hostname}",
        ]
        if self.alarm:
            lines.append("Warning : cpu over the temperature limit")
        return "\n".join(lines) + "\n"
