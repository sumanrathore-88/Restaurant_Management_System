# domain/logs.py
import os
import json
from datetime import datetime

DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
LOGS_JSON = os.path.join(DB_FOLDER, "logs.json")
LOGS_TXT = os.path.join(DB_FOLDER, "logs.txt")

def _format_datetime(dt=None, fmt="%Y-%m-%d %H:%M:%S"):
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)

def ensure_logs_exist():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER, exist_ok=True)
    if not os.path.exists(LOGS_JSON):
        with open(LOGS_JSON, "w") as f:
            json.dump([], f)
    if not os.path.exists(LOGS_TXT):
        open(LOGS_TXT, "a").close()

def log_event(level, message, actor=None):
    ensure_logs_exist()
    entry = {
        "timestamp": _format_datetime(),
        "level": level,
        "actor": actor,
        "message": message
    }
    # append to json list
    try:
        with open(LOGS_JSON, "r+") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception:
        pass

    # append to txt
    try:
        with open(LOGS_TXT, "a") as f:
            f.write(f"[{entry['timestamp']}] {level} - {actor or 'SYSTEM'} - {message}\n")
    except Exception:
        pass
