

import os
from datetime import datetime
from typing import List, Dict


GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
RESET = "\033[0m"
BOLD = "\033[1m"


try:
    from domain.validation import Validation
except Exception:
    class Validation:
        @staticmethod
        def validate_quantity(q):
            if not str(q).isdigit() or int(q) <= 0:
                raise ValueError("Quantity must be a positive integer.")
        @staticmethod
        def validate_payment_method(m):
            if m not in ("Cash", "Google Pay", "Netbanking"):
                raise ValueError("Invalid payment method.")

try:
    from domain.logs import Logger
except Exception:
    class Logger:
        @staticmethod
        def info(msg): print(f"[INFO] {msg}")
        @staticmethod
        def warn(msg): print(f"[WARN] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}")

try:
    from domain.table_booking import TableBooking
except Exception:
    TableBooking = None
    Logger.warn("table_booking.py not found. Table booking disabled.")



class MenuItem:
    def __init__(self, item_id: int, name: str, type_: str, half: float, full: float):
        self.id = item_id
        self.name = name
        self.type = type_
        self.half = half
        self.full = full


class Order:
    def __init__(self, staff_name="Staff"):
        self.staff_name = staff_name
        self.table_no = None
        self.items: List[Dict] = []
        self.total = 0.0

    def add_item(self, item: MenuItem, portion: str, qty: int):
        """Add selected menu item to order."""
        price = item.half if portion == "half" else item.full
        subtotal = price * qty
        self.items.append({
            "id": item.id,
            "name": item.name,
            "portion": portion,
            "qty": qty,
            "price": price,
            "amount": subtotal
        })
        self.total += subtotal



class Menu:
    def __init__(self):
        self.menu_items = self._load_menu_items()

    def _load_menu_items(self) -> List[MenuItem]:
        """Preload 50 Indian menu items."""
        items = [
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
        return [MenuItem(*i) for i in items]

    def display_menu(self):
        print(f"\n{CYAN}{BOLD}CHATORA MENU CARD (Veg = Green, Non-Veg = Red){RESET}")
        print("-" * 75)
        print(f"{'ID':<5}{'ITEM':<30}{'TYPE':<10}{'HALF':<10}{'FULL':<10}")
        print("-" * 75)
        for item in self.menu_items:
            color = GREEN if item.type == "Veg" else RED
            print(f"{color}{item.id:<5}{item.name:<30}{item.type:<10}{item.half:<10}{item.full:<10}{RESET}")
        print("-" * 75)

    # ========== MAIN ORDER FLOW ==========
    def take_order_interactive(self):
        """Interactive order flow called from registration.py"""
        self.display_menu()
        staff_name = input("Enter your (Staff/Admin) name: ").strip() or "Staff"
        order = Order(staff_name)

        # Optional Table Booking
        if TableBooking:
            choice = input("Would you like to book a table first? (y/n): ").strip().lower()
            if choice == "y":
                try:
                    tb = TableBooking()
                    booking = tb.book_table_interactive()
                    if booking:
                        order.table_no = booking.table_no
                except Exception as e:
                    Logger.warn(f"Table booking failed: {e}")

        # Add Menu Items
        while True:
            try:
                item_id = input("\nEnter Item ID to order (or 'done' to finish): ").strip()
                if item_id.lower() == "done":
                    break
                if not item_id.isdigit():
                    print("Please enter a valid Item ID.")
                    continue
                item_id = int(item_id)
                item = next((i for i in self.menu_items if i.id == item_id), None)
                if not item:
                    print("Invalid Item ID.")
                    continue

                portion = input("Enter portion (half/full): ").strip().lower()
                qty = int(input("Enter quantity: ").strip())
                Validation.validate_quantity(qty)

                order.add_item(item, portion, qty)
                print(f"Added {item.name} ({portion}) x {qty}")
            except Exception as e:
                Logger.warn(f"Error adding item: {e}")
                print(f"Error: {e}")

        if not order.items:
            print("No items ordered. Exiting.")
            return

        # Payment
        print(f"\nTotal Amount: ₹{order.total}")
        print("Payment Methods: 1) Cash  2) Google Pay  3) Netbanking")
        method = input("Select (1/2/3): ").strip()
        payment_map = {"1": "Cash", "2": "Google Pay", "3": "Netbanking"}
        pay_method = payment_map.get(method, "Cash")
        Validation.validate_payment_method(pay_method)

        # Print Bill
        self.print_bill(order, pay_method)
        Logger.info(f"Order completed for {staff_name}, Total ₹{order.total}")

    def print_bill(self, order: Order, payment_method: str):
        print(f"\n{BOLD}===== CHATORA BILL RECEIPT ====={RESET}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if order.table_no:
            print(f"Table No: {order.table_no}")
        print(f"Staff: {order.staff_name}")
        print("-" * 60)
        print(f"{'Item':<25}{'Qty':<5}{'Portion':<10}{'Price':<10}{'Amt':<10}")
        print("-" * 60)
        for i in order.items:
            print(f"{i['name']:<25}{i['qty']:<5}{i['portion']:<10}{i['price']:<10}{i['amount']:<10}")
        print("-" * 60)
        print(f"TOTAL AMOUNT: ₹{order.total}")
        print(f"Payment Method: {payment_method}")
        print("-" * 60)
        print("Thank you for dining at CHATORA!\n")



if __name__ == "__main__":
    Menu().take_order_interactive()
