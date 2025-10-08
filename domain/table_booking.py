
import json
import os
import datetime
from typing import List, Optional

from user_authentication import load_data, admin_authenticate
from menu_handling import MenuManager
from order import OrderManager, OrderItem, Order
from bill import BillManager, BillItem, Bill

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "database")
BOOKING_FILE = os.path.join(DB_DIR, "booking.json")

os.makedirs(DB_DIR, exist_ok=True)

# Constants
TOTAL_TABLES = 10
SEATS_PER_TABLE = 6
DEFAULT_DURATION_HOURS = 2  # default booking duration


def _now_iso():
    return datetime.datetime.now().isoformat()


def parse_datetime(date_str: str, time_str: str) -> Optional[datetime.datetime]:
    try:
        d = datetime.datetime.fromisoformat(f"{date_str}T{time_str}")
        return d
    except Exception:
        # try common formats
        try:
            d = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            return d
        except Exception:
            return None


class Booking:
    def __init__(self, booking_id: int, table_no: int, customer_name: str, contact: str, start: str, end: str, party_size: int, staff_id: Optional[int] = None):
        self.booking_id = booking_id
        self.table_no = table_no
        self.customer_name = customer_name
        self.contact = contact
        self.start = start  # ISO string
        self.end = end      # ISO string
        self.party_size = party_size
        self.staff_id = staff_id
        self.created_at = _now_iso()
        self.updated_at = self.created_at
        self.status = "CONFIRMED"  # CONFIRMED, CANCELLED
        self.order_id: Optional[int] = None
        self.bill_id: Optional[int] = None

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "table_no": self.table_no,
            "customer_name": self.customer_name,
            "contact": self.contact,
            "start": self.start,
            "end": self.end,
            "party_size": self.party_size,
            "staff_id": self.staff_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "order_id": self.order_id,
            "bill_id": self.bill_id,
        }

    @staticmethod
    def from_dict(d):
        b = Booking(d["booking_id"], d["table_no"], d["customer_name"], d["contact"], d["start"], d["end"], d["party_size"], d.get("staff_id"))
        b.created_at = d.get("created_at", b.created_at)
        b.updated_at = d.get("updated_at", b.updated_at)
        b.status = d.get("status", b.status)
        b.order_id = d.get("order_id")
        b.bill_id = d.get("bill_id")
        return b


class BookingManager:
    def __init__(self, menu_manager: MenuManager, order_manager: OrderManager, bill_manager: BillManager):
        self.menu_manager = menu_manager
        self.order_manager = order_manager
        self.bill_manager = bill_manager
        self.bookings: List[Booking] = []
        self._load()
        self._next_id = (max((b.booking_id for b in self.bookings), default=0) + 1) if self.bookings else 1

    def _load(self):
        if not os.path.exists(BOOKING_FILE):
            self.bookings = []
            return
        with open(BOOKING_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                self.bookings = []
                return
            raw = json.loads(content)
        self.bookings = [Booking.from_dict(d) for d in raw]

    def _save(self):
        with open(BOOKING_FILE, "w") as f:
            json.dump([b.to_dict() for b in self.bookings], f, indent=4)

    def _table_is_available(self, table_no: int, start: datetime.datetime, end: datetime.datetime) -> bool:
        for b in self.bookings:
            if b.table_no != table_no or b.status == "CANCELLED":
                continue
            existing_start = datetime.datetime.fromisoformat(b.start)
            existing_end = datetime.datetime.fromisoformat(b.end)
            # overlap check
            if (start < existing_end) and (end > existing_start):
                return False
        return True

    def available_tables(self, start: datetime.datetime, end: datetime.datetime) -> List[int]:
        available = []
        for t in range(1, TOTAL_TABLES + 1):
            if self._table_is_available(t, start, end):
                available.append(t)
        return available

    def create_booking(self, customer_name: str, contact: str, date_str: str, time_str: str, duration_hours: Optional[int], party_size: int, staff_id: Optional[int] = None) -> Optional[Booking]:
        dt = parse_datetime(date_str, time_str)
        if not dt:
            print("Invalid date/time format. Use YYYY-MM-DD and HH:MM (24-hr).")
            return None
        if duration_hours is None:
            duration_hours = DEFAULT_DURATION_HOURS
        start = dt
        end = dt + datetime.timedelta(hours=duration_hours)
        if party_size > SEATS_PER_TABLE:
            print(f"Party size exceeds seats per table ({SEATS_PER_TABLE}). Consider multiple tables or reduce party size.")
            return None
        avail = self.available_tables(start, end)
        if not avail:
            print("No tables available for the chosen slot.")
            return None
        table_no = avail[0]  # pick first available
        booking = Booking(self._next_id, table_no, customer_name, contact, start.isoformat(), end.isoformat(), party_size, staff_id)
        self._next_id += 1
        self.bookings.append(booking)
        self._save()
        print(f"Booked table {table_no} for {customer_name} on {start.isoformat()} (Booking id: {booking.booking_id})")
        return booking

    def find_booking(self, booking_id: int) -> Optional[Booking]:
        for b in self.bookings:
            if b.booking_id == booking_id:
                return b
        return None

    def list_bookings(self, include_cancelled: bool = False):
        for b in self.bookings:
            if not include_cancelled and b.status == "CANCELLED":
                continue
            self.print_booking(b)

    def print_booking(self, b: Booking):
        print("-" * 40)
        print(f"Booking ID: {b.booking_id} | Table: {b.table_no} | Customer: {b.customer_name} | Contact: {b.contact}")
        print(f"Party: {b.party_size} | Start: {b.start} | End: {b.end} | Status: {b.status}")
        print(f"Order ID: {b.order_id} | Bill ID: {b.bill_id}")

    # admin-only operations
    def modify_booking(self, booking_id: int, auth_data) -> bool:
        if not admin_authenticate(auth_data):
            return False
        b = self.find_booking(booking_id)
        if not b:
            print("Booking not found.")
            return False
        if b.status == "CANCELLED":
            print("Cannot modify a cancelled booking.")
            return False
        print("Current booking:")
        self.print_booking(b)
        print("Leave blank to keep current value.")
        new_name = input(f"New customer name [{b.customer_name}]: ").strip()
        new_contact = input(f"New contact [{b.contact}]: ").strip()
        new_date = input(f"New date (YYYY-MM-DD) [{b.start.split('T')[0]}]: ").strip()
        new_time = input(f"New time (HH:MM) [{b.start.split('T')[1][:5]}]: ").strip()
        new_duration = input("New duration hours (number) [leave blank to keep]: ").strip()
        new_party = input(f"New party size [{b.party_size}]: ").strip()

        # apply changes carefully and check availability
        start_dt = datetime.datetime.fromisoformat(b.start)
        end_dt = datetime.datetime.fromisoformat(b.end)

        if new_date or new_time or new_duration:
            date_val = new_date if new_date else start_dt.date().isoformat()
            time_val = new_time if new_time else start_dt.time().strftime("%H:%M")
            parsed = parse_datetime(date_val, time_val)
            if not parsed:
                print("Invalid new date/time format. Abort modification.")
                return False
            dur = int(new_duration) if new_duration else int((end_dt - start_dt).total_seconds() // 3600)
            new_start = parsed
            new_end = new_start + datetime.timedelta(hours=dur)
            # check availability for the same table excluding this booking
            conflict = False
            for other in self.bookings:
                if other.booking_id == b.booking_id or other.status == "CANCELLED":
                    continue
                if other.table_no != b.table_no:
                    continue
                o_start = datetime.datetime.fromisoformat(other.start)
                o_end = datetime.datetime.fromisoformat(other.end)
                if (new_start < o_end) and (new_end > o_start):
                    conflict = True
                    break
            if conflict:
                print("Requested new slot conflicts with another booking on the same table. Abort.")
                return False
            b.start = new_start.isoformat()
            b.end = new_end.isoformat()

        if new_name:
            b.customer_name = new_name
        if new_contact:
            b.contact = new_contact
        if new_party:
            try:
                p = int(new_party)
                if p > SEATS_PER_TABLE:
                    print(f"Party size exceeds table capacity ({SEATS_PER_TABLE}). Abort.")
                    return False
                b.party_size = p
            except ValueError:
                print("Invalid party size. Abort.")
                return False
        b.updated_at = _now_iso()
        self._save()
        print("Booking updated.")
        return True

    def cancel_booking(self, booking_id: int, auth_data) -> bool:
        if not admin_authenticate(auth_data):
            return False
        b = self.find_booking(booking_id)
        if not b:
            print("Booking not found.")
            return False
        if b.status == "CANCELLED":
            print("Booking already cancelled.")
            return False
        b.status = "CANCELLED"
        b.updated_at = _now_iso()
        self._save()
        print(f"Booking {booking_id} cancelled.")
        return True

    # Staff actions tied to booking
    def add_order_to_booking(self, booking_id: int):
        b = self.find_booking(booking_id)
        if not b:
            print("Booking not found.")
            return
        if b.status == "CANCELLED":
            print("Cannot add order to cancelled booking.")
            return
        # Create an order via order_manager and attach id
        order = self.order_manager.create_order(b.staff_id)
        print(f"Adding items to order id {order.order_id} for booking {booking_id}. Use menu to choose items.")
        self.menu_manager.list_menu()
        while True:
            id_choice = input("Enter dish id to add (blank to finish): ").strip()
            if not id_choice:
                break
            try:
                dish_id = int(id_choice)
            except ValueError:
                print("Invalid id.")
                continue
            item = self.menu_manager.find_by_id(dish_id)
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
        # save orders
        self.order_manager._save()
        b.order_id = order.order_id
        b.updated_at = _now_iso()
        self._save()
        print(f"Order {order.order_id} linked to booking {booking_id}.")

    def create_bill_for_booking(self, booking_id: int):
        b = self.find_booking(booking_id)
        if not b:
            print("Booking not found.")
            return
        if not b.order_id:
            print("No order attached to this booking. Create an order first.")
            return
        # Create bill from order using BillManager
        bill = self.bill_manager.create_bill_from_order(b.order_id, b.staff_id)
        if bill:
            b.bill_id = bill.bill_id
            b.updated_at = _now_iso()
            self._save()
            print(f"Bill {bill.bill_id} created and linked to booking {booking_id}.")


# ------------------
# CLI
# ------------------

def main():
    auth_data = load_data()
    menu_manager = MenuManager()
    order_manager = OrderManager(menu_manager)
    bill_manager = BillManager(order_manager)
    bm = BookingManager(menu_manager, order_manager, bill_manager)

    print("Table Booking System")
    print("1 - Staff: Create booking")
    print("2 - Staff: View booking by id")
    print("3 - Staff: List upcoming bookings")
    print("4 - Staff: Add order to booking")
    print("5 - Staff: Create bill for booking")
    print("6 - Admin: Modify booking")
    print("7 - Admin: Cancel booking")
    print("8 - Exit")

    while True:
        ch = input("Choose option (1-8): ").strip()
        if ch == "1":
            name = input("Customer name: ").strip()
            contact = input("Contact number: ").strip()
            date = input("Date (YYYY-MM-DD): ").strip()
            time = input("Time (HH:MM, 24-hr): ").strip()
            duration = input(f"Duration hours (default {DEFAULT_DURATION_HOURS}): ").strip()
            duration_val = int(duration) if duration else None
            try:
                party = int(input("Party size: ").strip())
            except ValueError:
                print("Invalid party size.")
                continue
            staffid = input("Staff id (optional): ").strip()
            try:
                sid = int(staffid) if staffid else None
            except ValueError:
                sid = None
            booking = bm.create_booking(name, contact, date, time, duration_val, party, sid)
            if booking:
                bm.print_booking(booking)

        elif ch == "2":
            try:
                bid = int(input("Enter booking id: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            b = bm.find_booking(bid)
            if not b:
                print("Booking not found.")
            else:
                bm.print_booking(b)

        elif ch == "3":
            bm.list_bookings()

        elif ch == "4":
            try:
                bid = int(input("Enter booking id to add order: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            bm.add_order_to_booking(bid)

        elif ch == "5":
            try:
                bid = int(input("Enter booking id to create bill: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            bm.create_bill_for_booking(bid)

        elif ch == "6":
            try:
                bid = int(input("Enter booking id to modify: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            bm.modify_booking(bid, auth_data)

        elif ch == "7":
            try:
                bid = int(input("Enter booking id to cancel: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            bm.cancel_booking(bid, auth_data)

        elif ch == "8":
            print("Goodbye")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()


