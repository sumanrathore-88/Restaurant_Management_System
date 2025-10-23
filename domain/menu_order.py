# domain/menu_order.py
import os
import json
from datetime import datetime
from .validation import (
    validate_non_empty_string,
    validate_email,
    validate_password,
    validate_id,
    validate_table_number,
    validate_payment_method,
    validate_quantity,
    format_datetime,
)
from .logs import log_event

# database file paths
DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
MENU_FILE = os.path.join(DB_FOLDER, "menu.json")
STAFF_FILE = os.path.join(DB_FOLDER, "staff.json")
ADMIN_FILE = os.path.join(DB_FOLDER, "admin.json")
ORDERS_FILE = os.path.join(DB_FOLDER, "orders.json")
TABLES_FILE = os.path.join(DB_FOLDER, "tables.json")

# ANSI colors
COLOR_RESET = "\u001b[0m"
COLOR_GREEN = "\u001b[32m"  # Veg
COLOR_RED = "\u001b[31m"    # Non-Veg
COLOR_YELLOW = "\u001b[33m" # Header/title

class MenuOrder:
    def __init__(self):
        os.makedirs(DB_FOLDER, exist_ok=True)
        self._ensure_files()
        self.menu = self._load_json(MENU_FILE)
        self.admin = self._load_json(ADMIN_FILE)
        self.staff = self._load_json(STAFF_FILE)
        self.orders = self._load_json(ORDERS_FILE)
        self.tables = self._load_json(TABLES_FILE)

    def _ensure_files(self):
        """Create database files if missing and populate defaults."""
        if not os.path.exists(ADMIN_FILE):
            admin = {
                "id": 100,
                "name": "suman rathore",
                "email": "suman@gmail.com",
                "password": "suman123",
            }
            with open(ADMIN_FILE, "w") as f:
                json.dump(admin, f, indent=2)

        if not os.path.exists(STAFF_FILE):
            with open(STAFF_FILE, "w") as f:
                json.dump([], f)

        if not os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "w") as f:
                json.dump([], f)

        if not os.path.exists(TABLES_FILE):
            tables = [{"table": i, "booked": False, "customer": None} for i in range(1, 21)]
            with open(TABLES_FILE, "w") as f:
                json.dump(tables, f, indent=2)

        if not os.path.exists(MENU_FILE):
            # generate 50 sample Indian items (alternating Veg/Non-Veg)
            base_items = [
                "Butter Chicken",
                "Paneer Butter Masala",
                "Chicken Biryani",
                "Veg Biryani",
                "Dal Makhani",
                "Chole Bhature",
                "Palak Paneer",
                "Mutton Rogan Josh",
                "Aloo Gobi",
                "Fish Curry",
            ]
            menu = []
            for i in range(1, 51):
                name = f"{base_items[(i - 1) % len(base_items)]} {i}"
                is_veg = (i % 2 == 0)
                half = 100 + (i * 2)
                full = int(half * 1.8)
                menu.append(
                    {
                        "id": i,
                        "item": name,
                        "type": "Veg" if is_veg else "Non-Veg",
                        "half": half,
                        "full": full,
                    }
                )
            with open(MENU_FILE, "w") as f:
                json.dump(menu, f, indent=2)

    def _load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            # for admin file return dict, others default to list
            return {} if path == ADMIN_FILE else []

    def _save_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _slug_item(self, name: str) -> str:
        """Convert name to lowercase underscores: 'Dal Makhani' -> 'dal_makhani'."""
        if not isinstance(name, str):
            return str(name)
        slug = "_".join(name.strip().lower().split())
        filtered = [ch for ch in slug if ch.isalnum() or ch == "_"]
        return "".join(filtered)

    def view_menu(self):
        """
        Print the menu in a colorful table-like form.
        Each line looks like: (48  mutton_rogan_josh  196  352)
        Veg items are shown in green, Non-Veg in red. A yellow header is printed once.
        """
        if not self.menu:
            print("Menu is empty.")
            return

        # Header
        header = f"{COLOR_YELLOW}({'ID':>3}  {'ITEM':<28}  {'HALF':>5}  {'FULL':>5}){COLOR_RESET}"
        print(header)
        print(f"{COLOR_YELLOW}{'-'*48}{COLOR_RESET}")

        for m in self.menu:
            mid = m.get("id")
            item_slug = self._slug_item(m.get("item", f"item_{mid}"))
            # limit item display width to 24 chars
            if len(item_slug) > 24:
                item_disp = item_slug[:21] + "..."
            else:
                item_disp = item_slug
            half = m.get("half", 0)
            full = m.get("full", 0)
            color = COLOR_GREEN if str(m.get("type", "")).lower().startswith("v") else COLOR_RED
            line = f"({mid:2d}  {item_disp:<24}  {half:4d}  {full:4d})"
            print(color + line + COLOR_RESET)

    def find_item(self, item_id):
        try:
            item_id = int(item_id)
        except Exception:
            return None
        for m in self.menu:
            if int(m.get("id", -1)) == item_id:
                return m
        return None

    def take_order(self, actor):
        """
        Robust interactive ordering (same behaviour as before).
        """
        order = {
            "order_id": len(self.orders) + 1,
            "actor": actor,
            "items": [],
            "total": 0,
            "datetime": format_datetime(),
        }

        print("\nEnter items (blank Item ID to finish).")
        try:
            while True:
                item_id = input("Item ID (blank to finish): ").strip()
                if item_id == "":
                    break
                if not item_id.isdigit():
                    print("Invalid id. Please enter a numeric ID (see View Menu).")
                    continue
                item = self.find_item(int(item_id))
                if not item:
                    print(f"Item not found for ID {item_id}.")
                    continue

                plate_type = input("Type (half/full): ").strip().lower()
                if plate_type not in ("half", "full"):
                    print("Invalid plate type. Enter 'half' or 'full'.")
                    continue

                qty = input("Quantity (positive integer): ").strip()
                if not validate_quantity(qty):
                    print("Invalid quantity. Enter a whole number > 0.")
                    continue
                qty = int(qty)

                price = item.get("half") if plate_type == "half" else item.get("full")
                subtotal = price * qty
                order["items"].append(
                    {
                        "id": item["id"],
                        "item": item["item"],
                        "type": item.get("type", ""),
                        "plate": plate_type,
                        "qty": qty,
                        "price_each": price,
                        "subtotal": subtotal,
                    }
                )
                order["total"] += subtotal
                print(f"Added: {qty} x {item['item']} ({plate_type}) — subtotal ₹{subtotal}")

            if not order["items"]:
                print("No items ordered. Cancelling.")
                return None

            # Confirm order summary before payment
            print("\nOrder summary:")
            for it in order["items"]:
                print(f"- {it['qty']} x {it['item']} ({it['plate']}) = ₹{it['subtotal']}")
            print(f"Total = ₹{order['total']}")

            attempts = 0
            while True:
                pm = input("Payment method (cash/google pay/gpay/netbanking): ").strip().lower()
                if validate_payment_method(pm):
                    break
                attempts += 1
                print("Invalid payment method. Use: cash, google pay (or gpay), netbanking.")
                if attempts >= 3:
                    print("Too many invalid payment attempts. Cancelling order.")
                    return None

            order["payment_method"] = pm
            order["paid"] = True

            # Save robustly
            try:
                self.orders.append(order)
                self._save_json(ORDERS_FILE, self.orders)
            except Exception as e:
                if self.orders and self.orders[-1].get("order_id") == order.get("order_id"):
                    self.orders.pop()
                print("Error saving order:", e)
                log_event("ERROR", f"Failed to save order {order.get('order_id')}: {e}", actor=actor.get("name"))
                return None

            log_event("INFO", f"Order taken id {order['order_id']} total {order['total']}", actor=actor.get("name"))
            self.print_bill(order)
            return order

        except KeyboardInterrupt:
            print("\nOrder interrupted by user. Cancelling.")
            return None
        except EOFError:
            print("\nInput terminated. Cancelling order.")
            return None
        except Exception as e:
            print("Unexpected error while taking order:", e)
            log_event("ERROR", f"Unexpected error during order: {e}", actor=actor.get("name"))
            return None

    def print_bill(self, order):
        print("\n" + "-" * 40)
        print("CHATORA - BILL")
        print(f"Order ID: {order.get('order_id')}   Date: {order.get('datetime')}")
        served_by = order.get("actor", {}).get("name", "Unknown")
        print(f"Served by: {served_by}")
        print("-" * 40)
        for it in order.get("items", []):
            name = it.get("item", "")[:20]
            plate = it.get("plate", "")
            qty = it.get("qty", 0)
            subtotal = it.get("subtotal", 0)
            print(f"{name:20s} {plate:4s} x{qty:2d}  ₹{subtotal:6d}")
        print("-" * 40)
        print(f"TOTAL: ₹{order.get('total')}")
        print(f"Payment: {order.get('payment_method')}")
        print("-" * 40 + "\n")

    def book_table(self, customer_name=None, contact=None):
        """Book a table 1..20 for a customer. Prompts for name, contact, date and time if not provided."""
        # Display current table status
        print("Tables (1..20) status:")
        for t in self.tables:
            st = "Booked" if t.get("booked") else "Available"
            print(f"Table {t.get('table'):2d}: {st}")

        # Collect booking details if not supplied
        if not customer_name:
            customer_name = input("Customer name: ").strip()
            if not customer_name:
                print("Customer name is required.")
                return None
        if not contact:
            contact = input("Contact number: ").strip()
            # basic validation: digits and length between 7 and 15
            if not (contact.isdigit() and 7 <= len(contact) <= 15):
                print("Invalid contact number. Use digits only (7-15 digits).")
                return None

        # Ask for date and time for booking
        # Expect date in YYYY-MM-DD and time in HH:MM (24-hour)
        date_str = input("Booking date (YYYY-MM-DD): ").strip()
        time_str = input("Booking time (HH:MM, 24-hour): ").strip()
        try:
            booking_dt = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
            booking_dt_str = booking_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            print("Invalid date/time format. Expected YYYY-MM-DD and HH:MM (24-hour).")
            return None

        # Choose table
        while True:
            choice = input("Enter table number to book (1-20): ").strip()
            if not validate_table_number(choice):
                print("Invalid table number.")
                continue
            choice = int(choice)
            selected = next((x for x in self.tables if x.get("table") == choice), None)
            if selected is None:
                print("Invalid table.")
                continue
            if selected.get("booked"):
                print("That table is already booked. Choose another.")
                continue

            # Book the table with details
            selected["booked"] = True
            selected["customer"] = {
                "name": customer_name,
                "contact": contact,
                "booking_datetime": booking_dt_str,
                "created_at": format_datetime(),
            }
            try:
                self._save_json(TABLES_FILE, self.tables)
            except Exception as e:
                print("Failed to save table booking:", e)
                log_event("ERROR", f"Failed to save table booking {choice}: {e}", actor=customer_name)
                return None

            log_event("INFO", f"Table {choice} booked by {customer_name} at {booking_dt_str}", actor=customer_name)
            print(f"Table {choice} successfully booked for {customer_name} on {booking_dt_str}.")
            return selected

    def admin_modify_menu(self, admin_actor):
        """Admin-only: add, update, remove menu items."""
        if not admin_actor or str(admin_actor.get("id")) != str(self.admin.get("id")):
            print("Only admin may modify the menu.")
            return

        print("Menu modification: 1) Add  2) Update  3) Remove  4) Exit")
        while True:
            ch = input("Choice: ").strip()
            if ch == "1":
                new_id = max((m.get("id", 0) for m in self.menu), default=0) + 1
                name = input("Item name: ").strip()
                typ = input("Type (Veg/Non-Veg): ").strip()
                try:
                    half = int(input("Half plate price: ").strip())
                    full = int(input("Full plate price: ").strip())
                except Exception:
                    print("Invalid price input.")
                    continue
                self.menu.append({"id": new_id, "item": name, "type": typ, "half": half, "full": full})
                self._save_json(MENU_FILE, self.menu)
                log_event("INFO", f"Admin added menu item {name}", actor=admin_actor.get("name"))
                print("Item added.")

            elif ch == "2":
                iid = input("Item id to update: ").strip()
                if not iid.isdigit():
                    print("Invalid id.")
                    continue
                it = self.find_item(int(iid))
                if not it:
                    print("Item not found.")
                    continue
                name = input(f"New name (blank keep '{it['item']}'): ").strip()
                typ = input(f"New type (blank keep '{it['type']}'): ").strip()
                half = input(f"Half price (blank keep {it['half']}): ").strip()
                full = input(f"Full price (blank keep {it['full']}): ").strip()
                if name:
                    it["item"] = name
                if typ:
                    it["type"] = typ
                if half:
                    try:
                        it["half"] = int(half)
                    except Exception:
                        pass
                if full:
                    try:
                        it["full"] = int(full)
                    except Exception:
                        pass
                self._save_json(MENU_FILE, self.menu)
                log_event("INFO", f"Admin updated menu id {iid}", actor=admin_actor.get("name"))
                print("Item updated.")

            elif ch == "3":
                iid = input("Item id to remove: ").strip()
                if not iid.isdigit():
                    print("Invalid id.")
                    continue
                iid = int(iid)
                self.menu = [m for m in self.menu if int(m.get("id", -1)) != iid]
                for idx, m in enumerate(self.menu, start=1):
                    m["id"] = idx
                self._save_json(MENU_FILE, self.menu)
                log_event("WARNING", f"Admin removed menu id {iid}", actor=admin_actor.get("name"))
                print("Item removed.")

            elif ch == "4":
                break
            else:
                print("Invalid choice.")

    def authenticate(self, user_id, password):
        """Authenticate admin or staff by id and password."""
        # admin
        if str(user_id) == str(self.admin.get("id")) and password == self.admin.get("password"):
            return {"id": self.admin.get("id"), "name": self.admin.get("name"), "role": "admin"}

        # staff
        for s in self.staff:
            if str(s.get("id")) == str(user_id) and s.get("password") == password:
                return {"id": s.get("id"), "name": s.get("name"), "role": "staff"}

        return None

    def add_staff(self, staff_obj, admin_actor):
        """Add staff (admin only). staff_obj should contain id, name, email, password, contact, qualification."""
        if not admin_actor or str(admin_actor.get("id")) != str(self.admin.get("id")):
            raise PermissionError("Only admin may add staff.")
        self.staff.append(staff_obj)
        self._save_json(STAFF_FILE, self.staff)
        log_event("INFO", f"New staff added: {staff_obj.get('name')}", actor=admin_actor.get("name"))
