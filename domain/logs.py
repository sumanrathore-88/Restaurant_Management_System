
import os
import threading
import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
LOG_FILE = os.path.join(DB_DIR, "logs.txt")


MAX_BYTES = 5 * 1024 * 1024


class Logger:
    

    def __init__(self, log_file: str = LOG_FILE, enable_console: bool = False):
        self.log_file = log_file
        self.enable_console = enable_console
        self.lock = threading.Lock()

        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, "a", encoding="utf-8"):
                pass

    # -----------------------------
    # Logging methods
    # -----------------------------
    def info(self, message: str):
        """Record informational messages."""
        self._write("INFO", message)

    def warning(self, message: str):
        """Record warnings."""
        self._write("WARNING", message)

    def error(self, message: str):
        """Record error messages."""
        self._write("ERROR", message)

    def exception(self, message: str, exc: Exception = None):
        """Record exception details with traceback."""
        try:
            trace = ""
            if exc:
                import traceback
                trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            self._write("EXCEPTION", f"{message}\n{trace}")
        except Exception as e:
            print(f"Logging exception failed: {e}")

    # -----------------------------
    # write logic
    # -----------------------------
    def _write(self, level: str, message: str):
        """Internal write method with file locking and rotation."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {level}: {message}"

        try:
            with self.lock:
                self._rotate_if_needed()
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

                if self.enable_console:
                    print(line)
        except Exception:
            try:
                print(line)  
            except Exception:
                pass

    # -----------------------------
    # 
    # -----------------------------
    def _rotate_if_needed(self):
        """If the log file exceeds MAX_BYTES, archive it."""
        try:
            if not os.path.exists(self.log_file):
                return
            if os.path.getsize(self.log_file) < MAX_BYTES:
                return

            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.log_file}.{ts}.backup"
            os.rename(self.log_file, backup_name)

            # Recreate empty log file
            with open(self.log_file, "a", encoding="utf-8"):
                pass

        except Exception:
            
            pass


# -------------------------------------------------------
_default_logger = None


def get_logger(enable_console: bool = False) -> Logger:
    
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger(enable_console=enable_console)
        _default_logger.info("Logger initialized (shared instance).")
    return _default_logger



if __name__ == "__main__":
    log = get_logger(enable_console=True)
    log.info("Test log entry - info")
    log.warning("Test log entry - warning")
    try:
        1 / 0
    except Exception as e:
        log.exception("Division by zero occurred", e)
