
from datetime import datetime, date, time, timedelta
import re
from typing import Optional, Union

#  constants
NUM_TABLES = 20
SEATS_PER_TABLE = 6
RESTAURANT_CAPACITY = 500
OPENING_TIME = time(hour=10, minute=0)   # 10:00
CLOSING_TIME = time(hour=22, minute=0)   # 22:00
MIN_HOURS = 1
MAX_HOURS = 4
MAX_ADVANCE_DAYS = 90   # roughly 3 months
MIN_PASSWORD_LENGTH = 4
MIN_NAME_LENGTH = 1

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Validation:

    @staticmethod
    def non_empty(value: Optional[str]) -> bool:
        """True if value is a non-empty string after stripping."""
        try:
            return bool(value and isinstance(value, str) and value.strip() != "")
        except Exception:
            return False

    # -----------------------
    # ID / numeric checks
    # -----------------------
    @staticmethod
    def is_valid_id(value: Union[str, int]) -> bool:
        """Positive integer ID check (accepts '123' or 123)."""
        try:
            if isinstance(value, int):
                return value > 0
            s = str(value).strip()
            if not s or not s.isdigit():
                return False
            return int(s) > 0
        except Exception:
            return False

    @staticmethod
    def is_positive_int(value: Union[str, int]) -> bool:
        """Non-negative integer (0 allowed)."""
        try:
            if isinstance(value, int):
                return value >= 0
            s = str(value).strip()
            if not s or not s.isdigit():
                return False
            return int(s) >= 0
        except Exception:
            return False

    # -----------------------
    # Contact / email / password
    # -----------------------
    @classmethod
    def is_valid_email(cls, email: Optional[str]) -> bool:
        """Basic email validation using regex."""
        try:
            if not cls.non_empty(email):
                return False
            return bool(EMAIL_REGEX.match(email.strip()))
        except Exception:
            return False

    @staticmethod
    def is_valid_password(pw: Optional[str]) -> bool:
        """Minimal password policy: at least MIN_PASSWORD_LENGTH printable chars."""
        try:
            if not pw or not isinstance(pw, str):
                return False
            return len(pw.strip()) >= MIN_PASSWORD_LENGTH
        except Exception:
            return False

    @staticmethod
    def is_valid_contact(contact: Optional[str]) -> bool:
        """
        Indian-style contact validation:
         - exactly 10 digits
         - digits only
        """
        try:
            if not contact:
                return False
            s = str(contact).strip()
            return bool(s.isdigit() and len(s) == 10)
        except Exception:
            return False

    # -----------------------
    # Menu / item validations
    # -----------------------
    @staticmethod
    def is_valid_item_name(name: Optional[str]) -> bool:
        """Non-empty name; reasonable max length enforced."""
        try:
            if not name or not isinstance(name, str):
                return False
            n = name.strip()
            return MIN_NAME_LENGTH <= len(n) <= 200
        except Exception:
            return False

    @staticmethod
    def is_valid_type(tp: Optional[str]) -> bool:
        """Accepts common spellings for Veg/Non-Veg (case-insensitive)."""
        try:
            if not tp or not isinstance(tp, str):
                return False
            t = tp.strip().lower()
            allowed = {
                "veg",
                "vegetarian",
                "non-veg",
                "non veg",
                "nonveg",
                "nonvegetarian",
                "non vegetarian",
                "nonvegetarian",
            }
            return t in allowed
        except Exception:
            return False

    @staticmethod
    def is_valid_price(val: Union[str, int, float]) -> bool:
        """Non-negative numeric price. Accepts numbers or numeric strings."""
        try:
            if isinstance(val, (int, float)):
                return float(val) >= 0.0
            s = str(val).strip()
            if not s:
                return False
            # allow a single decimal point
            if s.count(".") > 1:
                return False
            return bool(re.fullmatch(r"\d+(\.\d+)?", s)) and float(s) >= 0.0
        except Exception:
            return False

    @staticmethod
    def is_valid_quantity(q: Union[str, int]) -> bool:
        """Quantity limited to integer 1..5 inclusive."""
        try:
            if isinstance(q, int):
                return 1 <= q <= 5
            s = str(q).strip()
            if not s.isdigit():
                return False
            v = int(s)
            return 1 <= v <= 5
        except Exception:
            return False

    # -----------------------
    # Date/time checks
    # -----------------------
    @staticmethod
    def parse_date(s: str) -> Optional[date]:
        """
        Parse date in ISO format YYYY-MM-DD. Returns date or None on failure.
        """
        try:
            if not s or not isinstance(s, str):
                return None
            return datetime.strptime(s.strip(), "%Y-%m-%d").date()
        except Exception:
            return None

    @staticmethod
    def parse_time(s: str) -> Optional[time]:
        """
        Parse time in HH:MM (24-hour). Returns time or None on failure.
        """
        try:
            if not s or not isinstance(s, str):
                return None
            return datetime.strptime(s.strip(), "%H:%M").time()
        except Exception:
            return None

    @staticmethod
    def parse_datetime(s: str) -> Optional[datetime]:
       
        if not s or not isinstance(s, str):
            return None
        s2 = s.strip()
        fmts = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d")
        for fmt in fmts:
            try:
                return datetime.strptime(s2, fmt)
            except Exception:
                continue
        return None

    @staticmethod
    def within_opening_hours(start_t: time, hours: int) -> bool:
        
        try:
            if not isinstance(start_t, time):
                return False
            hours_i = int(hours)
            if hours_i < MIN_HOURS or hours_i > MAX_HOURS:
                return False
            dt_start = datetime.combine(date.today(), start_t)
            dt_end = dt_start + timedelta(hours=hours_i)
            start_ok = start_t >= OPENING_TIME
            end_ok = dt_end.time() <= CLOSING_TIME
            return start_ok and end_ok
        except Exception:
            return False

    @staticmethod
    def is_today_or_future_within_limit(d: date) -> bool:
        
        try:
            if not isinstance(d, date):
                return False
            today = date.today()
            if d < today:
                return False
            return d <= today + timedelta(days=MAX_ADVANCE_DAYS)
        except Exception:
            return False

    # -----------------------
    # Table / booking checks
    # -----------------------
    @staticmethod
    def is_valid_table_id(x: Union[str, int]) -> bool:
        """True if x corresponds to a table id between 1 and NUM_TABLES inclusive."""
        try:
            if isinstance(x, int):
                return 1 <= x <= NUM_TABLES
            s = str(x).strip()
            if not s.isdigit():
                return False
            v = int(s)
            return 1 <= v <= NUM_TABLES
        except Exception:
            return False

    @staticmethod
    def is_valid_person_count(x: Union[str, int]) -> bool:
        """Validate person count between 1 and RESTAURANT_CAPACITY."""
        try:
            if isinstance(x, int):
                return 1 <= x <= RESTAURANT_CAPACITY
            s = str(x).strip()
            if not s.isdigit():
                return False
            v = int(s)
            return 1 <= v <= RESTAURANT_CAPACITY
        except Exception:
            return False

    @staticmethod
    def is_valid_hours(x: Union[str, int]) -> bool:
        """Validate booking hours between MIN_HOURS and MAX_HOURS inclusive."""
        try:
            if isinstance(x, int):
                v = x
            else:
                s = str(x).strip()
                if not s.isdigit():
                    return False
                v = int(s)
            return MIN_HOURS <= v <= MAX_HOURS
        except Exception:
            return False

    # -----------------------
    # Reporting 
    # -----------------------
    @staticmethod
    def is_positive_number(x: Union[str, int, float]) -> bool:
        
        try:
            if isinstance(x, (int, float)):
                return float(x) >= 0.0
            s = str(x).strip()
            if not s:
                return False
            if s.count(".") > 1:
                return False
            if not re.fullmatch(r"\d+(\.\d+)?", s):
                return False
            return float(s) >= 0.0
        except Exception:
            return False
