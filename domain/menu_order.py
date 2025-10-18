# domain/menu_order.py
import json
import os
import sys
from typing import Dict, List, Any
from getpass import getpass
from datetime import datetime

from . import validation, logs

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
MENU_FILE = os.path.join(DB_PATH, "menu.json")
ORDERS_FILE = os.path.join(DB_PATH, "orders.json")


def _ensure_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH, exist_ok=True)
    # ensure orders file exists
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w") as f:
            json.dump({}, f, indent=2)


def default_menu_50() -> Dict[str, List[Any]]:
    """Return a 50-item Indian menu template.
       Format: "id": ["Item Name", half_price, full_price, "Veg"/"Non-Veg"]
    """
    items = [
        ("Butter Chicken", 150, 280, "Non-Veg"),
        ("Paneer Butter Masala", 120, 220, "Veg"),
        ("Dal Tadka", 80, 150, "Veg"),
        ("Veg Fried Rice", 70, 130, "Veg"),
        ("Chicken Biryani", 140, 260, "Non-Veg"),
        ("Mutton Biryani", 170, 320, "Non-Veg"),
        ("Aloo Gobi", 80, 140, "Veg"),
        ("Chole Bhature", 90, 160, "Veg"),
        ("Samosa (2 pcs)", 40, 70, "Veg"),
        ("Masala Dosa", 70, 130, "Veg"),
        ("Idli (2 pcs)", 40, 70, "Veg"),
        ("Vada Pav", 50, 90, "Veg"),
        ("Pav Bhaji", 80, 150, "Veg"),
        ("Paneer Tikka", 140, 260, "Veg"),
        ("Fish Curry", 150, 280, "Non-Veg"),
        ("Egg Curry", 90, 160, "Non-Veg"),
        ("Kadai Chicken", 160, 300, "Non-Veg"),
        ("Malai Kofta", 130, 240, "Veg"),
        ("Palak Paneer", 120, 220, "Veg"),
        ("Naan (2 pcs)", 40, 70, "Veg"),
        ("Rogan Josh", 170, 320, "Non-Veg"),
        ("Seekh Kebab (3 pcs)", 150, 280, "Non-Veg"),
        ("Tandoori Chicken (Half)", 220, 400, "Non-Veg"),
        ("Gulab Jamun (2 pcs)", 60, 100, "Veg"),
        ("Raita", 40, 70, "Veg"),
        ("Lassi (Sweet)", 50, 90, "Veg"),
        ("Paneer Paratha", 90, 160, "Veg"),
        ("Methi Mutter Malai", 120, 220, "Veg"),
        ("Aloo Paratha", 80, 140, "Veg"),
        ("Chicken 65", 150, 280, "Non-Veg"),
        ("Veg Manchurian", 110, 200, "Veg"),
        ("Chili Fish", 160, 300, "Non-Veg"),
        ("Schezwan Fried Rice", 90, 160, "Veg"),
        ("Chicken Noodles", 100, 180, "Non-Veg"),
        ("Murg Makhani", 160, 300, "Non-Veg"),
        ("Bhindi Masala", 90, 160, "Veg"),
        ("Kaddu Ki Sabzi", 80, 150, "Veg"),
        ("Tawa Pulao", 100, 180, "Veg"),
        ("Bombay Sandwich", 70, 130, "Veg"),
        ("Keema Pav", 130, 240, "Non-Veg"),
        ("Matar Paneer", 120, 220, "Veg"),
        ("Vegetable Korma", 110, 200, "Veg"),
        ("Chicken Shahi Korma", 180, 340, "Non-Veg"),
        ("Corn Chaat", 60, 100, "Veg"),
        ("Prawn Curry", 180, 340, "Non-Veg"),
        ("Kadhi Pakora", 90, 160, "Veg"),
        ("Sheer Khurma", 80, 150, "Veg"),
        ("Rabri", 90, 160, "Veg"),
    ]
    menu = {}
    for i, it in enumerate(items, start=1):
        menu[str(i)] = [it[0], it[1], it[2], it[3]]
    return menu


def create_menu_if_missing():
    _ensure_db()
    if not os.path.exists(MENU_FILE):
        menu = default_menu_50()
        with open(MENU_FILE, "w") as f:
            json.dump(menu, f, indent=2)
        logs.log_event("menu_created", "Default 50-item menu created", {"count": len(menu)})


def load_menu() -> Dict[str, List[Any]]:
    create_menu_if_missing()
    with open(MENU_FILE, "r") as f:
        return json.load(f)


def save_menu(menu: Dict[str, List[Any]]):
    _ensure_db()
    with open(MENU_FILE, "w") as f:
        json.dump(menu, f, indent=2)
    logs.log_event("menu_saved", "Menu saved/updated", {"count": len(menu)})


# ------------------------
# Terminal color helpers
# ------------------------
def _enable_windows_ansi_support():
    """Try to enable ANSI escape sequence processing on Windows."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            new_mode = mode.value | 0x0004
            kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        # If enabling fails, we still continue — the terminal may not support colors.
        pass


_enable_windows_ansi_support()

RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"


def _color_text(text: str, color_code: str) -> str:
    return f"{color_code}{text}{RESET}"


def _format_colored_cell(text: str, color_code: str, width: int) -> str:
    """
    Return a colored text padded to `width` characters when printed.
    We pad based on the raw text length (without ANSI codes) to ensure alignment.
    """
    raw_len = len(text)
    if raw_len > width:
        display = text[: max(0, width - 3)] + "..."
        raw_len = len(display)
    else:
        display = text
    colored = _color_text(display, color_code)
    padding = " " * (width - raw_len)
    return colored + padding


# ------------------------
# Menu display (table)
# ------------------------
def display_menu():
    """
    Print menu as a nicely formatted table with colored item names/types.
    Columns: ID, Item, Type, Half, Full
    """
    menu = load_menu()
    if not menu:
        print("Menu is empty.")
        return

    # compute widths (based on raw text, not colored length)
    id_w = max(2, max(len(str(k)) for k in menu.keys()))
    item_w = min(40, max(len(v[0]) for v in menu.values()))
    type_w = max(4, max(len(v[3]) for v in menu.values()))
    half_w = max(4, max(len(str(v[1])) for v in menu.values()))
    full_w = max(4, max(len(str(v[2])) for v in menu.values()))

    # header
    header_left = f"{'ID'.ljust(id_w)}  {'Item'.ljust(item_w)}  {'Type'.ljust(type_w)}"
    header_right = f"{'Half'.rjust(6)}  {'Full'.rjust(6)}"
    header = f"{BOLD}{CYAN}{header_left}  {header_right}{RESET}  {YELLOW}(Veg=Green,Non-Veg=Red){RESET}"
    # separator length: compute using raw widths + spaces and legend length
    sep_len = id_w + 2 + item_w + 2 + type_w + 2 + 6 + 2 + 6
    print(header)
    print("-" * (sep_len + 20))  # a little extra for legend

    # rows sorted by numeric id
    for mid in sorted(menu.keys(), key=lambda x: int(x)):
        name, half, full, typ = menu[mid]
        typ_clean = typ.strip()
        if typ_clean.lower().startswith("veg"):
            name_cell = _format_colored_cell(name, GREEN, item_w)
            type_cell = _format_colored_cell(typ_clean, GREEN, type_w)
        else:
            name_cell = _format_colored_cell(name, RED, item_w)
            type_cell = _format_colored_cell(typ_clean, RED, type_w)

        half_s = str(half).rjust(6)
        full_s = str(full).rjust(6)
        id_cell = str(mid).ljust(id_w)
        print(f"{id_cell}  {name_cell}  {type_cell}  {half_s}  {full_s}")

    print("-" * (sep_len + 20))
    print(f"{YELLOW}Tip: order by entering IDs (e.g. 1:full:2,5:half:1){RESET}")


# ------------------------
# Admin: add menu item
# ------------------------
def add_menu_item(admin_id: str):
    """Admin-only: add a menu item interactively."""
    # Authenticate
    pwd = getpass(prompt="Enter admin password to add item: ")
    if not validation.is_admin_credentials_valid(admin_id, pwd):
        logs.log_event(
            "auth_failed",
            "Attempt to add menu item failed - invalid admin credentials",
            {"admin_id": admin_id},
        )
        print("Invalid admin credentials. Action denied.")
        return False

    menu = load_menu()
    # collect details
    name = input("Item name: ").strip()
    half = input("Half plate price (integer): ").strip()
    full = input("Full plate price (integer): ").strip()
    typ = input("Type (Veg/Non-Veg): ").strip()
    # basic validation via validation module
    try:
        halfp = int(half)
        fullp = int(full)
    except Exception:
        print("Invalid price inputs. Aborting.")
        return False
    # compute next id
    next_id = str(max([int(i) for i in menu.keys()]) + 1 if menu else 1)
    menu[next_id] = [name, halfp, fullp, typ]
    save_menu(menu)
    logs.log_event("menu_item_added", f"Admin {admin_id} added menu item {name}", {"id": next_id})
    print(f"Item added with ID {next_id}")
    return True


# ------------------------
# Place order (staff)
# ------------------------
def place_order(staff_name: str) -> Dict[str, Any]:
    """
    Staff uses this to place an order. Returns order dict with totals.
    Order flow:
     - show menu
     - staff enters list of item_id:plate_type:qty triples (example: 1:full:2,3:half:1)
     - validate and compute total
     - take payment method and record
    """
    menu = load_menu()
    display_menu()
    raw = input("Enter items as comma separated triplets id:plate_type:qty (e.g. 1:full:2,3:half:1): ").strip()
    if not raw:
        print("No items specified.")
        return {}
    entries = [r.strip() for r in raw.split(",") if r.strip()]
    # parse
    order_lines = []
    for e in entries:
        parts = e.split(":")
        if len(parts) != 3:
            print(f"Invalid entry format: {e}. Skipping.")
            continue
        iid, plate, qty = parts
        if not validation.validate_plate_type(plate):
            print(f"Invalid plate type for item {iid}. Use 'half' or 'full'. Skipping.")
            continue
        if not validation.validate_quantity(qty):
            print(f"Invalid quantity for item {iid}. Skipping.")
            continue
        order_lines.append({"id": str(iid), "plate": plate.strip().lower(), "qty": int(qty)})

    if not order_lines:
        print("No valid order lines.")
        return {}

    if not validation.validate_item_ids([l["id"] for l in order_lines]):
        print("One or more item IDs are invalid. Aborting order.")
        return {}

    # compute bill
    subtotal = 0.0
    line_items = []
    for line in order_lines:
        item = menu[line["id"]]
        name = item[0]
        half_price = item[1]
        full_price = item[2]
        plate = line["plate"]
        qty = line["qty"]
        unit_price = half_price if plate == "half" else full_price
        amount = unit_price * qty
        subtotal += amount
        line_items.append(
            {
                "id": line["id"],
                "name": name,
                "plate": plate,
                "unit_price": unit_price,
                "qty": qty,
                "amount": amount,
            }
        )

    # taxes: 5% CGST + 5% SGST
    cgst = round(subtotal * 0.05, 2)
    sgst = round(subtotal * 0.05, 2)
    total = round(subtotal + cgst + sgst, 2)

    print("\n--- BILL ---")
    for li in line_items:
        print(f"{li['name']} ({li['plate']}) x{li['qty']} = {li['amount']}")
    print(f"Subtotal: {subtotal}")
    print(f"CGST (5%): {cgst}")
    print(f"SGST (5%): {sgst}")
    print(f"Total: {total}")

    # payment
    method = input("Payment method (UPI / Cash / Netbanking / Card): ").strip().lower()
    if not validation.validate_payment_method(method):
        print("Invalid payment method. Allowed: upi, cash, netbanking, card. Aborting.")
        return {}

    payment_ref = None
    if method == "upi":
        payment_ref = input("Enter UPI transaction id / reference: ").strip()
    elif method == "netbanking":
        payment_ref = input("Enter netbanking transaction id: ").strip()
    elif method == "card":
        payment_ref = input("Enter last 4 digits of card or txn ref: ").strip()
    elif method == "cash":
        payment_ref = "cash_received"

    # save order
    _ensure_db()
    orders = {}
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            try:
                orders = json.load(f)
            except Exception:
                orders = {}
    # generate order id
    next_oid = str(max([int(i) for i in orders.keys()]) + 1) if orders else "1"
    order_record = {
        "order_id": next_oid,
        "staff": staff_name,
        "lines": line_items,
        "subtotal": subtotal,
        "cgst": cgst,
        "sgst": sgst,
        "total": total,
        "payment_method": method,
        "payment_ref": payment_ref,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    orders[next_oid] = order_record
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

    logs.log_event("order_placed", f"Order {next_oid} placed by staff {staff_name}", {"order_id": next_oid, "total": total})
    print(f"Order placed successfully. Order ID: {next_oid}")
    return order_record
