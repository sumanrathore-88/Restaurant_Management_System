
import json
import os
from datetime import datetime
from typing import Any, Dict

LOGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOGS_PATH, "logs.json")


def _ensure_log_file():
    if not os.path.exists(LOGS_PATH):
        os.makedirs(LOGS_PATH, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)


def _read_logs():
    _ensure_log_file()
    with open(LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _write_logs(logs):
    _ensure_log_file()
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def log_event(event_type: str, message: str, data: Dict[str, Any] = None):
    """Write a structured log entry to logs.json and print to console."""
    _ensure_log_file()
    logs = _read_logs()
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "message": message,
        "data": data or {},
    }
    logs.append(entry)
    _write_logs(logs)
    # Console feedback (helpful during development/running)
    print(f"[{entry['timestamp']}] {event_type.upper()}: {message}")


def get_recent_logs(limit: int = 20):
    logs = _read_logs()
    return logs[-limit:]
