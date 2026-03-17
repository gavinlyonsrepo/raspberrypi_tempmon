"""
notifiers.py
Outbound notifications: email via msmtp, desktop via notify-send.
Each function is self-contained and handles its own errors gracefully
so a notification failure never crashes the main monitoring loop.
"""

import os
import subprocess
import smtplib
from email.message import EmailMessage

from . import display
from .config import CACHE_DIR

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def send_mail(subject: str, cfg) -> None:
    """Send log.txt as an email attachment using smtplib.
    Requires SMTP_PASSWORD to be a Gmail App Password.
    """
    log_path = os.path.join(CACHE_DIR, "log.txt")

    if not cfg.smtp.password:
        display.error("SMTP_PASSWORD is not set in config file.")
        display.error("Set up a Gmail App Password and add it to rpi_tempmon.cfg")
        return

    if not os.path.exists(log_path):
        display.error(f"Log file not found at {log_path} — run -l first.")
        return

    try:
        # Build the message
        msg = EmailMessage()
        msg["Subject"] = f"rpi-tempmon: {subject}"
        msg["From"]    = cfg.mail_user
        msg["To"]      = cfg.mail_user
        msg.set_content("Raspberry Pi temperature log attached.")

        # Attach log.txt
        with open(log_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="text",
                subtype="plain",
                filename="log.txt",
            )

        # Send via Gmail SMTP
        with smtplib.SMTP(cfg.smtp.server, cfg.smtp.port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(cfg.mail_user, cfg.smtp.password)
            smtp.send_message(msg)

        display.bold("Mail sent successfully.")

    except smtplib.SMTPAuthenticationError:
        display.error("Gmail authentication failed.")
        display.error("Make sure SMTP_PASSWORD is a Gmail App Password, not your regular password.")
        display.error("Generate one at: myaccount.google.com → Security → App passwords")
    except smtplib.SMTPException as exc:
        display.error(f"SMTP error: {exc}")
    except OSError as exc:
        display.error(f"Network or file error: {exc}")


# ---------------------------------------------------------------------------
# Desktop notifications
# ---------------------------------------------------------------------------

def notify(mode: str, cpu_temp: float, cpu_limit: int) -> None:
    """Send a desktop notification via notify-send.

    mode '2' — always notify with current CPU temperature.
    mode '3' — only notify when cpu_temp exceeds cpu_limit.

    Requires libnotify-bin:
        sudo apt install libnotify-bin
    """
    title = "rpi_tempmon"

    if mode == "2":
        message = f"CPU temperature => {cpu_temp}'C"
        _send_notify(title, message)

    elif mode == "3":
        if cpu_temp > cpu_limit:
            message = f"ALARM: CPU temp {cpu_temp}'C — limit is {cpu_limit}'C"
            _send_notify(title, message)
    else:
        display.error(f"Invalid -n argument '{mode}'. Use 2 (always) or 3 (alarm only).")


def _send_notify(title: str, message: str) -> None:
    try:
        subprocess.run(
            ["notify-send", title, message],
            timeout=5,
            check=True,
        )
    except FileNotFoundError:
        display.error("notify-send not found. Install with: sudo apt install libnotify-bin")
    except subprocess.TimeoutExpired:
        display.error("notify-send timed out.")
    except subprocess.CalledProcessError as exc:
        display.error(f"notify-send failed: {exc}")
