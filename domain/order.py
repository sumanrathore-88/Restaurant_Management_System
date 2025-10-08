
import json
import os
import datetime
from typing import List, Dict, Optional

from user_authentication import load_data, admin_authenticate
from menu_handling import MenuManager, MenuItem

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "database")
ORDERS_FILE = os.path.join(DB_DIR, "order.json")

os.makedirs(DB_DIR, exist_ok=True)


def _now_iso() -> str:
    return datetime.datetime.now().isoformat()


class OrderItem:
    def __init__(self, dish_id: int, dish_name: str, portion: str, qty: int, unit_price: int):
        self.dish_id = dish_id
        self.dish_name = dish_name
        self.portion = portion  # 'h' or 'f'
        self.qty = qty
        self.unit_price = unit_price

    def to_dict(self) -> Dict:
        return {
            "dish_id": self.dish_id,
            "dish_name": self.dish_name,
            "portion": self.portion,
            "qty": self.qty,
            "unit_price": self.unit_price,
        }

    @staticmethod
    def from_dict(d: Dict) -> "OrderItem":
        return OrderItem(d["dish_id"], d["dish_name"], d["portion"], d["qty"], d["unit_price"])


class Order:
    def __init__(self, order_id: int, staff_id: Optional[int] = None):
        self.order_id = order_id
        self.staff_id = staff_id
        self.items: List[OrderItem] = []
        self.created_at = _now_iso()
        self.status = "OPEN"  # OPEN, COMPLETED, CANCELLED
        self.updated_at = self.created_at

    def add_item(self, item: OrderItem):
        self.items.append(item)
        self.updated_at = _now_iso()

    def total(self) -> int:
        return sum(it.qty * it.unit_price for it in self.items)

    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "staff_id": self.staff_id,
            "items": [it.to_dict() for it in self.items],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Order":
        o = Order(d["order_id"], d.get("staff_id"))
        o.items = [OrderItem.from_dict(it) for it in d.get("items", [])]
        o.created_at = d.get("created_at", o.created_at)
        o.updated_at = d.get("updated_at", o.updated_at)
        o.status = d.get("status", "OPEN")
        return o


class OrderManager:
    def __init__(self, menu_manager: MenuManager):
        self.menu_manager = menu_manager
        self.orders: List[Order] = []
        self._load()
        self._next_id = (max((o.order_id for o in self.orders), default=0) + 1) if self.orders else 1

    def _load(self):
        if not os.path.exists(ORDERS_FILE):
            self.orders = []
            return
        with open(ORDERS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                self.orders = []
                return
            raw = json.loads(content)
        self.orders = [Order.from_dict(d) for d in raw]

    def _save(self):
        with open(ORDERS_FILE, "w") as f:
            json.dump([o.to_dict() for o in self.orders], f, indent=4)

    def create_order(self, staff_id: Optional[int] = None) -> Order:
        order = Order(self._next_id, staff_id)
        self._next_id += 1
        self.orders.append(order)
        self._save()
        return order

    def find_order(self, order_id: int) -> Optional[Order]:
        for o in self.orders:
            if o.order_id == order_id:
                return o
        return None

    def list_orders(self, include_cancelled: bool = True) -> List[Order]:
        if include_cancelled:
            return list(self.orders)
        return [o for o in self.orders if o.status != "CANCELLED"]

    def cancel_order(self, order_id: int, auth_data) -> bool:
        if not admin_authenticate(auth_data):
            return False
        o = self.find_order(order_id)
        if not o:
            print("Order not found.")
            return False
        if o.status == "CANCELLED":
            print("Order already cancelled.")
            return False
        o.status = "CANCELLED"
        o.updated_at = _now_iso()
        self._save()
        print(f"Order {order_id} cancelled.")
        return True

    def modify_order(self, order_id: int, auth_data) -> bool:
        # Admin only
        if not admin_authenticate(auth_data):
            return False
        o = self.find_order(order_id)
        if not o:
            print("Order not found.")
            return False
        if o.status == "CANCELLED":
            print("Cannot modify a cancelled order.")
            return False
        print("Modifying order. Current items:")
        self.print_order(o)
        print("Choose operation: \n 1 - Add item\n 2 - Remove item (by index)\n 3 - Change quantity (by index)")
        choice = input("Option (1/2/3): ").strip()
        if choice == "1":
            self._admin_add_item_to_order(o)
        elif choice == "2":
            try:
                idx = int(input("Index to remove (starting 1): ").strip()) - 1
            except ValueError:
                print("Invalid index.")
                return False
            if 0 <= idx < len(o.items):
                removed = o.items.pop(idx)
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
            if 0 <= idx < len(o.items) and new_qty > 0:
                o.items[idx].qty = new_qty
                print("Quantity updated.")
            else:
                print("Index out of range or invalid quantity.")
                return False
        else:
            print("Invalid choice.")
            return False
        o.updated_at = _now_iso()
        self._save()
        print("Order modified.")
        return True

    def _admin_add_item_to_order(self, order: Order):
        self.menu_manager.list_menu()
        try:
            dish_id = int(input("Dish id to add: ").strip())
        except ValueError:
            print("Invalid id.")
            return
        item = self.menu_manager.find_by_id(dish_id)
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
        order.add_item(OrderItem(item.id, item.dish, portion, qty, unit_price))

    def print_order(self, order: Order):
        print(f"Order ID: {order.order_id} | Status: {order.status} | Created: {order.created_at} | Updated: {order.updated_at}")
        print(f"Taken by staff id: {order.staff_id}")
        print("Items:")
        if not order.items:
            print("  (no items)")
        for i, it in enumerate(order.items, start=1):
            line = it.qty * it.unit_price
            print(f" {i}. {it.dish_name} ({'Half' if it.portion=='h' else 'Full'}) x {it.qty} @ ₹{it.unit_price} = ₹{line}")
        print("TOTAL: ₹" + str(order.total()))


# ------------------
# CLI for staff/admin
# ------------------

def main():
    auth_data = load_data()
    menu_manager = MenuManager()
    om = OrderManager(menu_manager)

    print("Order Management System")
    print("1 - Staff: Create new order")
    print("2 - Staff: View order by id")
    print("3 - List all orders")
    print("4 - Admin: Modify order")
    print("5 - Admin: Cancel order")
    print("6 - Exit")

    while True:
        ch = input("Choose option (1-6): ").strip()
        if ch == "1":
            try:
                staff_id_input = input("Enter your staff id (optional): ").strip()
                staff_id = int(staff_id_input) if staff_id_input else None
            except ValueError:
                print("Invalid staff id. Will record as None.")
                staff_id = None
            order = om.create_order(staff_id)
            print(f"Created order with id {order.order_id}. Add items (leave dish id blank to finish).")
            menu_manager.list_menu()
            while True:
                id_choice = input("Enter dish id to add (blank to finish): ").strip()
                if not id_choice:
                    break
                try:
                    dish_id = int(id_choice)
                except ValueError:
                    print("Invalid id.")
                    continue
                item = menu_manager.find_by_id(dish_id)
                if not item:
                    print("Dish not found.")
                    continue
                portion = input("Portion - half or full? (h/f): ").strip().lower()
                if portion not in ("h", "f"):
                    print("Invalid portion.")
                    continue
                try:
                    qty = int(input("Quantity: ").strip())
                except ValueError:
                    print("Invalid quantity.")
                    continue
                unit_price = (item.half_rate_min + item.half_rate_max) // 2 if portion == "h" else (item.full_rate_min + item.full_rate_max) // 2
                order.add_item(OrderItem(item.id, item.dish, portion, qty, unit_price))
                print(f"Added {qty} x {item.dish} at ₹{unit_price} each")
            print("Order summary:")
            om.print_order(order)
            om._save()

        elif ch == "2":
            try:
                oid = int(input("Enter order id: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            o = om.find_order(oid)
            if not o:
                print("Order not found.")
            else:
                om.print_order(o)

        elif ch == "3":
            orders = om.list_orders()
            if not orders:
                print("No orders.")
            for o in orders:
                print("-" * 40)
                om.print_order(o)

        elif ch == "4":
            try:
                oid = int(input("Enter order id to modify: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            om.modify_order(oid, auth_data)

        elif ch == "5":
            try:
                oid = int(input("Enter order id to cancel: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            om.cancel_order(oid, auth_data)

        elif ch == "6":
            print("Goodbye")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()

