# domain/validation.py
import re
from datetime import datetime

def validate_non_empty_string(s):
    return isinstance(s, str) and s.strip() != ""

def validate_email(email):
    # simple email validation
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_password(pw):
    return isinstance(pw, str) and len(pw) >= 4

def validate_id(i):
    try:
        return int(i) >= 0
    except Exception:
        return False

def validate_table_number(n):
    try:
        n = int(n)
        return 1 <= n <= 20
    except Exception:
        return False

def validate_payment_method(pm):
    return pm.lower() in ("cash", "google pay", "gpay", "netbanking")

def validate_quantity(q):
    try:
        q = int(q)
        return q > 0
    except Exception:
        return False

def format_datetime(dt=None, fmt="%Y-%m-%d %H:%M:%S"):
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)
