

import os
import sys
import traceback
from datetime import datetime


RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"


BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "database", "logs"))
os.makedirs(BASE_DIR, exist_ok=True)
LOG_FILE = os.path.join(BASE_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")


class Logger:
   

    LOG_LEVELS = ["INFO", "WARN", "ERROR", "CRITICAL"]

    @staticmethod
    def _timestamp():
        """Return current timestamp string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _write_to_file(level: str, message: str):
        """Append a formatted log entry to today's log file."""
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{Logger._timestamp()}] [{level}] {message}\n")
        except Exception as e:
            # Do not crash on log errors; just print a fallback
            print(f"[LoggerError] Failed to write to log file: {e}", file=sys.stderr)

    @staticmethod
    def _print_to_console(level: str, message: str):
        """Print colored log output to console."""
        color = {
            "INFO": GREEN,
            "WARN": YELLOW,
            "ERROR": RED,
            "CRITICAL": MAGENTA
        }.get(level, RESET)

        print(f"{color}[{Logger._timestamp()}] [{level}] {message}{RESET}")

    @classmethod
    def log(cls, level: str, message: str):
        
        level = level.upper()
        if level not in cls.LOG_LEVELS:
            level = "INFO"
        formatted = f"{message}"
        cls._write_to_file(level, formatted)
        cls._print_to_console(level, formatted)

    
    @classmethod
    def info(cls, message: str):
        cls.log("INFO", message)

    @classmethod
    def warn(cls, message: str):
        cls.log("WARN", message)

    @classmethod
    def error(cls, message: str):
        cls.log("ERROR", message)

    @classmethod
    def critical(cls, message: str):
        cls.log("CRITICAL", message)

    @classmethod
    def exception(cls, exc: Exception, context: str = ""):
        """Log full traceback of an exception safely."""
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        msg = f"{context}\n{tb}" if context else tb
        cls.log("ERROR", msg)



if __name__ == "__main__":
    Logger.info("Logger test: system started.")
    Logger.warn("Logger test: low stock warning.")
    try:
        1 / 0
    except Exception as e:
        Logger.exception(e, "Test exception occurred in logs.py")
    Logger.critical("Logger test: system shutdown imminent.")
    print(f"Logs written to: {LOG_FILE}")
