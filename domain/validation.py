# domain/validation.py
import json
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
USERS_FILE = os.path.join(DB_PATH, "users.json")
MENU_FILE = os.path.join(DB_PATH, "menu.json")
TABLES_FILE = os.path.join(DB_PATH, "tables.json")

ALLOWED_PAYMENT_METHODS = {"upi", "cash", "netbanking", "card"}


def _ensure_db_folders():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH, exist_ok=True)


def load_users():
    _ensure_db_folders()
    if not os.path.exists(USERS_FILE):
        # default admin
        users = {
            "100": {
                "id": 100,
                "name": "suman rathore",
                "email": "suman@gmail.com",
                "password": "suman123"
            }
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return users
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def is_admin_credentials_valid(admin_id: str, password: str) -> bool:
    """
    Check whether provided admin id/password are valid.
    All if/else decisions for authentication live here.
    """
    users = load_users()
    if admin_id in users:
        if users[admin_id].get("password") == password:
            return True
        else:
            return False
    else:
        return False


def validate_payment_method(method: str) -> bool:
    """Return True if method is allowed — all branching here."""
    if not isinstance(method, str):
        return False
    method = method.strip().lower()
    if method in ALLOWED_PAYMENT_METHODS:
        return True
    else:
        return False


def load_menu() -> Dict[str, List[Any]]:
    """Load menu JSON — if missing, menu should be created elsewhere."""
    _ensure_db_folders()
    if not os.path.exists(MENU_FILE):
        return {}
    with open(MENU_FILE, "r") as f:
        return json.load(f)


def validate_item_ids(item_ids: List[str]) -> bool:
    """Check provided item ids exist in menu."""
    menu = load_menu()
    if not menu:
        return False
    for iid in item_ids:
        if str(iid) not in menu:
            return False
    return True


def validate_quantity(qty: int) -> bool:
    """Quantity must be positive integer."""
    try:
        q = int(qty)
    except Exception:
        return False
    if q <= 0:
        return False
    return True


def validate_plate_type(plate_type: str) -> bool:
    """Accept 'half' or 'full'."""
    if not isinstance(plate_type, str):
        return False
    t = plate_type.strip().lower()
    if t in ("half", "full"):
        return True
    return False


def load_tables() -> Dict[str, Any]:
    _ensure_db_folders()
    if not os.path.exists(TABLES_FILE):
        # create 20 tables by default
        tables = {str(i): {"table_no": i, "booked": False, "name": None, "phone": None} for i in range(1, 21)}
        with open(TABLES_FILE, "w") as f:
            json.dump(tables, f, indent=2)
        return tables
    with open(TABLES_FILE, "r") as f:
        return json.load(f)


def is_table_available(table_no: int) -> bool:
    tables = load_tables()
    tno = str(table_no)
    if tno not in tables:
        return False
    if tables[tno].get("booked") is True:
        return False
    return True


def validate_table_number(table_no: int) -> bool:
    try:
        t = int(table_no)
    except Exception:
        return False
    tables = load_tables()
    return str(t) in tables


def get_table_status(table_no: int) -> dict:
    tables = load_tables()
    return tables.get(str(table_no), {})
