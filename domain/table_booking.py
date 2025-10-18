# domain/table_booking.py
import json
import os
from getpass import getpass
from typing import Dict, Any

from . import validation, logs, menu_order

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
TABLES_FILE = os.path.join(DB_PATH, "tables.json")
ORDERS_FILE = os.path.join(DB_PATH, "orders.json")


def _ensure_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH, exist_ok=True)
    # ensure tables file exists via validation.load_tables()
    validation.load_tables()


def view_menu():
    menu_order.display_menu()


def book_table():
    _ensure_db()
    name = input("Customer name: ").strip()
    phone = input("Customer phone: ").strip()
    table_no = input("Table number to book (1-20): ").strip()
    try:
        tno = int(table_no)
    except Exception:
        print("Invalid table number.")
        return False
    if not validation.validate_table_number(tno):
        print("Table number does not exist.")
        return False
    if not validation.is_table_available(tno):
        print(f"Table {tno} is already booked.")
        return False
    tables = validation.load_tables()
    tables[str(tno)]["booked"] = True
    tables[str(tno)]["name"] = name
    tables[str(tno)]["phone"] = phone
    with open(TABLES_FILE, "w") as f:
        json.dump(tables, f, indent=2)
    logs.log_event("table_booked", f"Table {tno} booked for {name}", {"table_no": tno, "name": name, "phone": phone})
    print(f"Table {tno} successfully booked.")
    return True


def cancel_booking(admin_id: str):
    """Admin only: cancel a booking."""
    pwd = getpass(prompt="Enter admin password to cancel booking: ")
    if not validation.is_admin_credentials_valid(admin_id, pwd):
        logs.log_event("auth_failed", "Attempt to cancel booking failed - invalid admin credentials", {"admin_id": admin_id})
        print("Invalid admin credentials. Action denied.")
        return False
    tno = input("Table number to cancel booking: ").strip()
    try:
        t = int(tno)
    except Exception:
        print("Invalid table number.")
        return False
    if not validation.validate_table_number(t):
        print("Table number does not exist.")
        return False
    tables = validation.load_tables()
    tables[str(t)]["booked"] = False
    tables[str(t)]["name"] = None
    tables[str(t)]["phone"] = None
    with open(TABLES_FILE, "w") as f:
        json.dump(tables, f, indent=2)
    logs.log_event("booking_cancelled", f"Admin {admin_id} cancelled booking for table {t}", {"table_no": t})
    print(f"Booking for table {t} cancelled.")
    return True


def take_order_and_pay(staff_name: str, table_no: int = None):
    """
    If table_no provided, ensure that table is booked or allow placing order for walk-in.
    Then delegate to menu_order.place_order for ordering & billing.
    """
    _ensure_db()
    if table_no:
        if not validation.validate_table_number(table_no):
            print("Invalid table number.")
            return {}
        # if booked, we can continue
        status = validation.get_table_status(table_no)
        if status.get("booked"):
            print(f"Table {table_no} is booked for {status.get('name')}. Proceeding to take order.")
        else:
            print(f"Table {table_no} is not booked. Proceeding as walk-in.")

    order = menu_order.place_order(staff_name)
    if not order:
        print("No order generated.")
        return {}

    # Optionally link order to table
    if table_no:
        # attach table info into orders.json
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r") as f:
                try:
                    orders = json.load(f)
                except Exception:
                    orders = {}
        else:
            orders = {}
        oid = order["order_id"]
        if oid in orders:
            orders[oid]["table_no"] = table_no
        else:
            # order may have been returned but not saved; safest to save again
            orders[oid] = order
            orders[oid]["table_no"] = table_no
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)
        logs.log_event("order_table_linked", f"Order {oid} linked to table {table_no}", {"order_id": oid, "table_no": table_no})

    return order
