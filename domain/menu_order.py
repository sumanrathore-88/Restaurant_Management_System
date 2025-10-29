import os
import json
import getpass
from datetime import datetime
from typing import List, Dict, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # package root (RESTAURANT_MANAGEMENT_SYSTEM/domain -> ..)
DB_DIR = os.path.join(BASE_DIR, "database")
MENU_FILE = os.path.join(DB_DIR, "menu.json")

# Admin  (must match registration module)
ADMIN = {
    "id": 100,
    "name": "suman rathore",
    "email": "suman@gmail.com",
    "password": "suman123",
}

# Initial items (from user)
INITIAL_ITEMS = [
    (1, "Butter Chicken", "Non-Veg", 150, 280),
    (2, "Paneer Butter Masala", "Veg", 120, 220),
    (3, "Dal Makhani", "Veg", 90, 160),
    (4, "Chicken Biryani", "Non-Veg", 130, 250),
    (5, "Veg Pulao", "Veg", 100, 180),
    (6, "Mutton Rogan Josh", "Non-Veg", 180, 320),
    (7, "Shahi Paneer", "Veg", 130, 230),
    (8, "Malai Kofta", "Veg", 120, 210),
    (9, "Fish Curry", "Non-Veg", 160, 300),
    (10, "Chole Bhature", "Veg", 80, 150),
    (11, "Tandoori Chicken", "Non-Veg", 170, 320),
    (12, "Kadai Paneer", "Veg", 120, 220),
    (13, "Rajma Chawal", "Veg", 90, 160),
    (14, "Egg Curry", "Non-Veg", 100, 180),
    (15, "Palak Paneer", "Veg", 110, 200),
    (16, "Chicken Tikka", "Non-Veg", 150, 280),
    (17, "Veg Fried Rice", "Veg", 90, 160),
    (18, "Mutton Biryani", "Non-Veg", 180, 320),
    (19, "Paneer Tikka", "Veg", 130, 230),
    (20, "Prawn Masala", "Non-Veg", 180, 340),
    (21, "Aloo Gobi", "Veg", 90, 160),
    (22, "Mix Veg Curry", "Veg", 100, 180),
    (23, "Keema Curry", "Non-Veg", 160, 290),
    (24, "Kadhi Pakoda", "Veg", 80, 150),
    (25, "Chicken Korma", "Non-Veg", 150, 280),
    (26, "Paneer Lababdar", "Veg", 130, 230),
    (27, "Methi Malai Matar", "Veg", 110, 200),
    (28, "Fish Fry", "Non-Veg", 150, 280),
    (29, "Chana Masala", "Veg", 90, 160),
    (30, "Veg Biryani", "Veg", 110, 200),
    (31, "Chicken Curry", "Non-Veg", 140, 260),
    (32, "Paneer Do Pyaza", "Veg", 120, 220),
    (33, "Egg Biryani", "Non-Veg", 120, 220),
    (34, "Masala Dosa", "Veg", 80, 150),
    (35, "Idli Sambar", "Veg", 70, 130),
    (36, "Vada Pav", "Veg", 40, 70),
    (37, "Pav Bhaji", "Veg", 90, 160),
    (38, "Bhel Puri", "Veg", 50, 90),
    (39, "Samosa Chaat", "Veg", 60, 110),
    (40, "Mutton Curry", "Non-Veg", 180, 320),
    (41, "Fish Biryani", "Non-Veg", 170, 310),
    (42, "Chicken 65", "Non-Veg", 150, 270),
    (43, "Paneer Roll", "Veg", 90, 160),
    (44, "Veg Burger", "Veg", 70, 130),
    (45, "Chicken Burger", "Non-Veg", 100, 180),
    (46, "Veg Momos", "Veg", 80, 140),
    (47, "Chicken Momos", "Non-Veg", 90, 160),
    (48, "Paneer Pakoda", "Veg", 80, 150),
    (49, "Aloo Tikki", "Veg", 60, 110),
    (50, "Gulab Jamun", "Veg", 50, 90),
]

# -------------------------
# Try to import Validation & Logger from domain; 
# -------------------------
try:
    from domain.validation import Validation
except Exception:
    
    class Validation:
        @staticmethod
        def is_valid_id(val) -> bool:
            try:
                return int(val) > 0
            except Exception:
                return False

        @staticmethod
        def is_valid_item_name(name: str) -> bool:
            return bool(name and name.strip())

        @staticmethod
        def is_valid_type(tp: str) -> bool:
            return tp.lower() in {"veg", "non-veg", "nonveg", "nonveg", "non veg", "veg"}

        @staticmethod
        def is_valid_price(val) -> bool:
            try:
                return float(val) >= 0
            except Exception:
                return False

        @staticmethod
        def is_valid_quantity(q) -> bool:
            try:
                q = int(q)
                return 1 <= q <= 5
            except Exception:
                return False

        @staticmethod
        def non_empty(value: str) -> bool:
            return bool(value and value.strip())

try:
    from domain.logs import Logger
except Exception:
    # fallback minimal logger
    import datetime

    class Logger:
        def __init__(self):
            os.makedirs(DB_DIR, exist_ok=True)
            self._path = os.path.join(DB_DIR, "logs.txt")

        def _write(self, level: str, msg: str):
            line = f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] {level}: {msg}\n"
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                print(line, end="")

        def info(self, msg: str):
            self._write("INFO", msg)

        def warning(self, msg: str):
            self._write("WARNING", msg)

        def error(self, msg: str):
            self._write("ERROR", msg)


# ------------------------
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDER = "\033[4m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"
    BG_GRAY = "\033[47m"


# -------------------------
# MenuOrder class
# -------------------------
class MenuOrder:
    def __init__(self, menu_path: str = MENU_FILE):
        self.menu_path = menu_path
        os.makedirs(os.path.dirname(self.menu_path), exist_ok=True)
        self.validation = Validation()
        self.logger = Logger()

        self.menu = self._load_or_seed_menu()

    # -------------------------

    def _load_or_seed_menu(self) -> List[Dict]:

        if os.path.exists(self.menu_path):
            try:
                with open(self.menu_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    self.logger.warning("menu.json had invalid format; reseeding.")
            except Exception as e:
                self.logger.error(f"Failed to load menu.json: {e}")

        seeded = []
        for tup in INITIAL_ITEMS:
            item = {
                "id": int(tup[0]),
                "name": tup[1],
                "type": tup[2],  # "Veg" or "Non-Veg"
                "half": float(tup[3]),
                "full": float(tup[4]),
            }
            seeded.append(item)
        self._save_menu(seeded)
        self.logger.info("Seeded menu.json with initial items.")
        return seeded

    def _save_menu(self, menu_list: List[Dict]) -> bool:
        try:
            with open(self.menu_path, "w", encoding="utf-8") as f:
                json.dump(menu_list, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save menu.json: {e}")
            return False

    # -------------------------
    def _find_item_by_id(self, item_id: int) -> Optional[Dict]:
        for it in self.menu:
            if int(it.get("id")) == int(item_id):
                return it
        return None

    def _next_id(self) -> int:
        if not self.menu:
            return 1
        return max(int(i["id"]) for i in self.menu) + 1

    # -------------------------
    
    def display_menu(self):
        # header
        print(Colors.BOLD + Colors.CYAN + "\nCHATORA_RESTAURANT MENU" + Colors.RESET)
        header = f"{'ID':<4} {'Item':<30} {'Type':<10} {'Half':>6} {'Full':>6}"
        print(Colors.UNDER + header + Colors.RESET)
        # rows
        for it in sorted(self.menu, key=lambda x: int(x["id"])):
            tid = str(it["id"]).ljust(4)
            name = (it["name"][:28] + "..") if len(it["name"]) > 30 else it["name"].ljust(30)
            typ = it["type"]
            
            color = Colors.GREEN if typ.lower().startswith("veg") else Colors.RED
            half = f"{it['half']:.0f}".rjust(6)
            full = f"{it['full']:.0f}".rjust(6)
            print(f"{tid} {name} {color}{typ:<10}{Colors.RESET} {half} {full}")
        print()

    # -------------------------
    # Ordering & Billing
    # -------------------------
    def take_order(self):
        try:
            self.display_menu()
            print("Place order — choose items by ID. Enter blank line to finish.")
            order_items: List[Tuple[Dict, str, int, float]] = []
            # Each order entry: (item_dict, plate_type('half'/'full'), quantity, line_total)
            while True:
                sid = input("Item ID (blank to finish): ").strip()
                if sid == "":
                    break
                if not self.validation.is_valid_id(sid):
                    print("Invalid ID format. Try again.")
                    continue
                item = self._find_item_by_id(int(sid))
                if not item:
                    print("No item with that ID. Try again.")
                    continue
                plate_type = input("Plate type (half/full): ").strip().lower()
                if plate_type not in {"half", "full"}:
                    print("Plate type must be 'half' or 'full'.")
                    continue
                qty = input("Quantity (1-5): ").strip()
                if not self.validation.is_valid_quantity(qty):
                    print("Quantity must be an integer between 1 and 5.")
                    continue
                qty_i = int(qty)
                price_per = item["half"] if plate_type == "half" else item["full"]
                line_total = price_per * qty_i
                order_items.append((item, plate_type, qty_i, line_total))
                print(f"Added: {item['name']} x{qty_i} ({plate_type}) -> {line_total:.2f}")

            if not order_items:
                print("No items ordered.")
                return

            # compute totals
            subtotal = sum(line[3] for line in order_items)
            # simple tax/service example: 5% tax + 2% service
            tax = subtotal * 0.05
            service = subtotal * 0.02
            total = subtotal + tax + service

            # payment
            print("\nPayment methods: 1. Cash  2. Google Pay  3. Netbanking")
            pay_choice = input("Choose payment method (1/2/3): ").strip()
            pay_map = {"1": "Cash", "2": "Google Pay", "3": "Netbanking"}
            payment_method = pay_map.get(pay_choice, None)
            if payment_method is None:
                print("Invalid payment method. Defaulting to Cash.")
                payment_method = "Cash"

            # timestamp
            order_time = datetime.now().isoformat(sep=" ", timespec="seconds")

            # generate bill
            print(Colors.BOLD + Colors.MAGENTA + "\n------- BILL -------" + Colors.RESET)
            print(f"CHATORA_RESTAURANT\tTime: {order_time}")
            print("-" * 40)
            for item, plate, qty, line_total in order_items:
                name = item["name"]
                typ = item["type"]
                print(f"{name} ({plate}) x{qty} -> {line_total:.2f} [{typ}]")
            print("-" * 40)
            print(f"Subtotal: {subtotal:.2f}")
            print(f"Tax (5%): {tax:.2f}")
            print(f"Service (2%): {service:.2f}")
            print(Colors.BOLD + f"Total: {total:.2f}" + Colors.RESET)
            print(f"Payment Method: {payment_method}")
            print("--------------------\n")

            # log the order
            try:
                order_log = {
                    "timestamp": order_time,
                    "items": [
                        {"id": int(i[0]["id"]), "name": i[0]["name"], "plate": i[1], "qty": i[2], "line_total": i[3]}
                        for i in order_items
                    ],
                    "subtotal": subtotal,
                    "tax": tax,
                    "service": service,
                    "total": total,
                    "payment_method": payment_method,
                }
                
                orders_log_path = os.path.join(DB_DIR, "orders.json")
                existing = []
                if os.path.exists(orders_log_path):
                    try:
                        with open(orders_log_path, "r", encoding="utf-8") as f:
                            existing = json.load(f) or []
                    except Exception:
                        existing = []
                existing.append(order_log)
                with open(orders_log_path, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2)
                self.logger.info(f"New order placed at {order_time} - total {total:.2f}")
            except Exception as e:
                self.logger.error(f"Failed to save order log: {e}")

        except Exception as e:
            print("An error occurred while taking order.")
            self.logger.error(f"Exception in take_order: {e}")

    # -------------------------
    # Admin operations: add/update/delete
    # -------------------------
    def _admin_authenticate(self) -> bool:
        try:
            print("Admin authentication required.")
            admin_id = input("Admin ID: ").strip()
            admin_email = input("Admin Email: ").strip()
            admin_pw = getpass.getpass("Admin Password: ").strip()
            if not (self.validation.is_valid_id(admin_id) and self.validation.non_empty(admin_email)):
                print("Invalid admin credential format.")
                return False
            if int(admin_id) == ADMIN["id"] and admin_email.lower() == ADMIN["email"].lower() and admin_pw == ADMIN["password"]:
                self.logger.info("Admin authenticated for menu changes.")
                return True
            else:
                print("Admin authentication failed.")
                self.logger.warning("Admin authentication failed for menu change attempt.")
                return False
        except Exception as e:
            self.logger.error(f"Exception in admin auth: {e}")
            return False

    def add_item(self):
        if not self._admin_authenticate():
            return
        try:
            nid = self._next_id()
            print(f"Adding new item with ID {nid}")
            name = input("Item name: ").strip()
            if not self.validation.is_valid_item_name(name):
                print("Invalid name.")
                return
            typ = input("Type (Veg/Non-Veg): ").strip()
            if not self.validation.is_valid_type(typ):
                print("Type must be 'Veg' or 'Non-Veg'.")
                return
            half = input("Half plate price: ").strip()
            if not self.validation.is_valid_price(half):
                print("Invalid price for half.")
                return
            full = input("Full plate price: ").strip()
            if not self.validation.is_valid_price(full):
                print("Invalid price for full.")
                return
            new_item = {"id": nid, "name": name, "type": typ.title(), "half": float(half), "full": float(full)}
            self.menu.append(new_item)
            if self._save_menu(self.menu):
                print("Item added successfully.")
                self.logger.info(f"Admin added menu item {nid} - {name}")
            else:
                print("Failed to save new item.")
        except Exception as e:
            print("An error occurred while adding item.")
            self.logger.error(f"Exception in add_item: {e}")

    def update_item(self):
        if not self._admin_authenticate():
            return
        try:
            sid = input("Enter Item ID to update: ").strip()
            if not self.validation.is_valid_id(sid):
                print("Invalid ID.")
                return
            item = self._find_item_by_id(int(sid))
            if not item:
                print("Item not found.")
                return
            print(f"Updating item {item['id']} - {item['name']}")
            name = input(f"Name [{item['name']}]: ").strip() or item['name']
            typ = input(f"Type [{item['type']}]: ").strip() or item['type']
            if not self.validation.is_valid_type(typ):
                print("Invalid type.")
                return
            half = input(f"Half [{item['half']}]: ").strip() or str(item['half'])
            if not self.validation.is_valid_price(half):
                print("Invalid half price.")
                return
            full = input(f"Full [{item['full']}]: ").strip() or str(item['full'])
            if not self.validation.is_valid_price(full):
                print("Invalid full price.")
                return
            # update fields
            item['name'] = name
            item['type'] = typ.title()
            item['half'] = float(half)
            item['full'] = float(full)
            if self._save_menu(self.menu):
                print("Item updated.")
                self.logger.info(f"Admin updated menu item {sid}")
            else:
                print("Failed to save updated item.")
        except Exception as e:
            print("An error occurred while updating item.")
            self.logger.error(f"Exception in update_item: {e}")

    def delete_item(self):
        if not self._admin_authenticate():
            return
        try:
            sid = input("Enter Item ID to delete: ").strip()
            if not self.validation.is_valid_id(sid):
                print("Invalid ID.")
                return
            item = self._find_item_by_id(int(sid))
            if not item:
                print("Item not found.")
                return
            confirm = input(f"Confirm delete {item['id']} - {item['name']}? (y/N): ").strip().lower()
            if confirm != "y":
                print("Deletion cancelled.")
                return
            self.menu = [i for i in self.menu if int(i['id']) != int(sid)]
            if self._save_menu(self.menu):
                print("Item deleted.")
                self.logger.info(f"Admin deleted menu item {sid}")
            else:
                print("Failed to save after deletion.")
        except Exception as e:
            print("An error occurred while deleting item.")
            self.logger.error(f"Exception in delete_item: {e}")

    # -------------------------
    
    def main(self):
        try:
            while True:
                print(Colors.BOLD + Colors.BLUE + "\nMENU/ORDER MODULE" + Colors.RESET)
                print("1. View Menu")
                print("2. Take Order (Staff/Admin)")
                print("3. Admin - Add Item")
                print("4. Admin - Update Item")
                print("5. Admin - Delete Item")
                print("6. Back/Exit")
                choice = input("Choose: ").strip()
                if choice == "1":
                    self.display_menu()
                elif choice == "2":
                    self.take_order()
                elif choice == "3":
                    self.add_item()
                elif choice == "4":
                    self.update_item()
                elif choice == "5":
                    self.delete_item()
                elif choice == "6":
                    break
                else:
                    print("Invalid choice.")
        except Exception as e:
            print("Menu module encountered an error.")
            self.logger.error(f"Exception in menu main loop: {e}")

if __name__ == "__main__":
    mo = MenuOrder()
    try:
        mo.main()
    except KeyboardInterrupt:
        print("\nExiting menu module.")
    except Exception as e:
        mo.logger.error(f"Fatal error in domain.menu_order __main__: {e}")
