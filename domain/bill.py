
import json
import os
import datetime
from typing import List, Dict, Optional

from user_authentication import load_data, admin_authenticate
from order import OrderManager, Order, OrderItem
from menu_handling import MenuManager

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "database")
BILLS_FILE = os.path.join(DB_DIR, "bill.json")
ORDERS_FILE = os.path.join(DB_DIR, "order.json")

os.makedirs(DB_DIR, exist_ok=True)


def _now_iso() -> str:
    return datetime.datetime.now().isoformat()


class BillItem:
    def __init__(self, dish_id: int, dish_name: str, portion: str, qty: int, unit_price: int):
        self.dish_id = dish_id
        self.dish_name = dish_name
        self.portion = portion
        self.qty = qty
        self.unit_price = unit_price

    def to_dict(self) -> Dict:
        return {
            "dish_id": self.dish_id,
            "dish_name": self.dish_name,
            "portion": self.portion,
            "qty": self.qty,
            "unit_price": self.unit_price,
            "line_total": self.qty * self.unit_price,
        }

    @staticmethod
    def from_dict(d: Dict) -> "BillItem":
        return BillItem(d["dish_id"], d["dish_name"], d["portion"], d["qty"], d["unit_price"])


class Bill:
    def __init__(self, bill_id: int, order_id: int, staff_id: Optional[int] = None):
        self.bill_id = bill_id
        self.order_id = order_id
        self.staff_id = staff_id
        self.items: List[BillItem] = []
        self.created_at = _now_iso()
        self.updated_at = self.created_at
        self.status = "OPEN"  # OPEN, PAID, CANCELLED

    def add_item(self, item: BillItem):
        self.items.append(item)
        self.updated_at = _now_iso()

    def subtotal(self) -> int:
        return sum(it.qty * it.unit_price for it in self.items)

    def to_dict(self) -> Dict:
        return {
            "bill_id": self.bill_id,
            "order_id": self.order_id,
            "staff_id": self.staff_id,
            "items": [it.to_dict() for it in self.items],
            "subtotal": self.subtotal(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Bill":
        b = Bill(d["bill_id"], d["order_id"], d.get("staff_id"))
        b.items = [BillItem.from_dict(it) for it in d.get("items", [])]
        b.created_at = d.get("created_at", b.created_at)
        b.updated_at = d.get("updated_at", b.updated_at)
        b.status = d.get("status", "OPEN")
        return b


class BillManager:
    def __init__(self, order_manager: OrderManager):
        self.order_manager = order_manager
        self.bills: List[Bill] = []
        self._load()
        self._next_id = (max((b.bill_id for b in self.bills), default=0) + 1) if self.bills else 1

    def _load(self):
        if not os.path.exists(BILLS_FILE):
            self.bills = []
            return
        with open(BILLS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                self.bills = []
                return
            raw = json.loads(content)
        self.bills = [Bill.from_dict(d) for d in raw]

    def _save(self):
        with open(BILLS_FILE, "w") as f:
            json.dump([b.to_dict() for b in self.bills], f, indent=4)

    def create_bill_from_order(self, order_id: int, staff_id: Optional[int] = None) -> Optional[Bill]:
        order = self.order_manager.find_order(order_id)
        if not order:
            print("Order not found.")
            return None
        if order.status == "CANCELLED":
            print("Cannot bill a cancelled order.")
            return None
        # Create bill
        bill = Bill(self._next_id, order_id, staff_id)
        self._next_id += 1
        for it in order.items:
            bill.add_item(BillItem(it.dish_id, it.dish_name, it.portion, it.qty, it.unit_price))
        self.bills.append(bill)
        self._save()
        print(f"Bill {bill.bill_id} created for order {order_id} with subtotal ₹{bill.subtotal()}.")
        return bill

    def find_bill(self, bill_id: int) -> Optional[Bill]:
        for b in self.bills:
            if b.bill_id == bill_id:
                return b
        return None

    def list_bills(self, include_cancelled: bool = True) -> List[Bill]:
        if include_cancelled:
            return list(self.bills)
        return [b for b in self.bills if b.status != "CANCELLED"]

    def cancel_bill(self, bill_id: int, auth_data) -> bool:
        if not admin_authenticate(auth_data):
            return False
        b = self.find_bill(bill_id)
        if not b:
            print("Bill not found.")
            return False
        if b.status == "CANCELLED":
            print("Bill already cancelled.")
            return False
        b.status = "CANCELLED"
        b.updated_at = _now_iso()
        self._save()
        print(f"Bill {bill_id} cancelled.")
        return True

    def modify_bill(self, bill_id: int, auth_data) -> bool:
        # Admin-only
        if not admin_authenticate(auth_data):
            return False
        b = self.find_bill(bill_id)
        if not b:
            print("Bill not found.")
            return False
        if b.status == "CANCELLED":
            print("Cannot modify a cancelled bill.")
            return False
        print("Current bill items:")
        self.print_bill(b)
        print("Operations:\n 1 - Add item\n 2 - Remove item (by index)\n 3 - Change quantity (by index)")
        choice = input("Option (1/2/3): ").strip()
        if choice == "1":
            self._admin_add_item_to_bill(b)
        elif choice == "2":
            try:
                idx = int(input("Index to remove (starting 1): ").strip()) - 1
            except ValueError:
                print("Invalid index.")
                return False
            if 0 <= idx < len(b.items):
                removed = b.items.pop(idx)
                print(f"Removed {removed.dish_name}.")
            else:
                print("Index out of range.")
                return False
        elif choice == "3":
            try:
                idx = int(input("Index to change (starting 1): ").strip()) - 1
                new_qty = int(input("New quantity: ").strip())
            except ValueError:
                print("Invalid input.")
                return False
            if 0 <= idx < len(b.items) and new_qty > 0:
                b.items[idx].qty = new_qty
                print("Quantity updated.")
            else:
                print("Index out of range or invalid quantity.")
                return False
        else:
            print("Invalid choice.")
            return False
        b.updated_at = _now_iso()
        self._save()
        print("Bill modified.")
        return True

    def _admin_add_item_to_bill(self, bill: Bill):
        self.order_manager.menu_manager.list_menu()
        try:
            dish_id = int(input("Dish id to add: ").strip())
        except ValueError:
            print("Invalid id.")
            return
        item = self.order_manager.menu_manager.find_by_id(dish_id)
        if not item:
            print("Dish id not found.")
            return
        portion = input("Portion (h/f): ").strip().lower()
        if portion not in ("h", "f"):
            print("Invalid portion.")
            return
        try:
            qty = int(input("Quantity: ").strip())
        except ValueError:
            print("Invalid quantity.")
            return
        unit_price = (item.half_rate_min + item.half_rate_max) // 2 if portion == "h" else (item.full_rate_min + item.full_rate_max) // 2
        bill.add_item(BillItem(item.id, item.dish, portion, qty, unit_price))

    def print_bill(self, bill: Bill):
        print(f"Bill ID: {bill.bill_id} | Order ID: {bill.order_id} | Status: {bill.status}")
        print(f"Created: {bill.created_at} | Updated: {bill.updated_at}")
        print(f"Taken by staff id: {bill.staff_id}")
        if not bill.items:
            print("  (no items)")
        for i, it in enumerate(bill.items, start=1):
            line = it.qty * it.unit_price
            print(f" {i}. {it.dish_name} ({'Half' if it.portion=='h' else 'Full'}) x {it.qty} @ ₹{it.unit_price} = ₹{line}")
        print("SUBTOTAL: ₹" + str(bill.subtotal()))


# ------------------
# CLI
# ------------------

def main():
    auth_data = load_data()
    menu_manager = MenuManager()
    order_manager = OrderManager(menu_manager)
    bm = BillManager(order_manager)

    print("Billing System")
    print("1 - Staff: Create bill from order")
    print("2 - View bill by id")
    print("3 - List all bills")
    print("4 - Admin: Modify bill")
    print("5 - Admin: Cancel bill")
    print("6 - Exit")

    while True:
        ch = input("Choose option (1-6): ").strip()
        if ch == "1":
            try:
                oid = int(input("Enter order id to bill: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            sid_input = input("Staff id (optional): ").strip()
            try:
                sid = int(sid_input) if sid_input else None
            except ValueError:
                sid = None
            bill = bm.create_bill_from_order(oid, sid)
            if bill:
                bm.print_bill(bill)

        elif ch == "2":
            try:
                bid = int(input("Enter bill id: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            b = bm.find_bill(bid)
            if not b:
                print("Bill not found.")
            else:
                bm.print_bill(b)

        elif ch == "3":
            bills = bm.list_bills()
            if not bills:
                print("No bills.")
            for b in bills:
                print("-" * 40)
                bm.print_bill(b)

        elif ch == "4":
            try:
                bid = int(input("Enter bill id to modify: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            bm.modify_bill(bid, auth_data)

        elif ch == "5":
            try:
                bid = int(input("Enter bill id to cancel: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            bm.cancel_bill(bid, auth_data)

        elif ch == "6":
            print("Goodbye")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()

