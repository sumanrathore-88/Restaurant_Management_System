from __future__ import annotations
import os
import json
import getpass
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional, Set

# Constants
NUM_TABLES = 20
SEATS_PER_TABLE = 6
RESTAURANT_CAPACITY = 500

# Restaurant open/close
RESTAURANT_OPEN = time(hour=10, minute=0)    # 10:00
RESTAURANT_CLOSE = time(hour=22, minute=0)   # 22:00

# Booking START window (user request): bookings may start only between 10:00 and 18:00
BOOKING_START_ALLOWED = time(hour=10, minute=0)  # 10:00
BOOKING_START_LAST = time(hour=18, minute=0)     # 18:00

MIN_HOURS = 1
MAX_HOURS = 4
MAX_ADVANCE_DAYS = 90  # ~3 months

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
BOOKING_FILE = os.path.join(DB_DIR, "bookings.json")

# Admin 
ADMIN = {"id": 100, "name": "suman rathore", "email": "suman@gmail.com", "password": "suman123"}

# Try to import Validation and Logger; 
try:
    from domain.validation import Validation
except Exception:
    class Validation:
        @staticmethod
        def non_empty(x): return bool(x and str(x).strip())
        @staticmethod
        def parse_date(s):
            try: return datetime.strptime(s.strip(), "%Y-%m-%d").date()
            except Exception: return None
        @staticmethod
        def parse_time(s):
            try: return datetime.strptime(s.strip(), "%H:%M").time()
            except Exception: return None
        @staticmethod
        def is_valid_hours(x):
            try:
                v = int(x); return 1 <= v <= MAX_HOURS
            except Exception: return False
        @staticmethod
        def is_today_or_future_within_limit(d: date) -> bool:
            try:
                today = date.today()
                return (d >= today) and (d <= today + timedelta(days=MAX_ADVANCE_DAYS))
            except Exception:
                return False
        @staticmethod
        def is_valid_person_count(x):
            try:
                v = int(x); return 1 <= v <= RESTAURANT_CAPACITY
            except Exception:
                return False
        @staticmethod
        def is_valid_contact(c):
            try:
                s = str(c).strip(); return s.isdigit() and len(s) == 10
            except Exception:
                return False
        @staticmethod
        def is_valid_id(x):
            try: return int(x) > 0
            except Exception: return False
        @staticmethod
        def within_opening_hours(start_t: time, hours: int) -> bool:
            
            try:
                dt_start = datetime.combine(date.today(), start_t)
                dt_end = dt_start + timedelta(hours=int(hours))
                return (start_t >= RESTAURANT_OPEN) and (dt_end.time() <= RESTAURANT_CLOSE)
            except Exception:
                return False

try:
    from domain.logs import get_logger
    logger = get_logger()
except Exception:
    import datetime
    class SimpleLogger:
        def __init__(self):
            os.makedirs(DB_DIR, exist_ok=True)
            self.path = os.path.join(DB_DIR, "logs.txt")
        def _write(self, level, msg):
            try:
                ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(f"[{ts}] {level}: {msg}\n")
            except Exception:
                try: print(f"{level}: {msg}")
                except Exception: pass
        def info(self, m): self._write("INFO", m)
        def warning(self, m): self._write("WARNING", m)
        def error(self, m): self._write("ERROR", m)
    logger = SimpleLogger()

try:
    from domain.menu_order import MenuOrder
except Exception:
    MenuOrder = None


def _intervals_overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return (a_start < b_end) and (a_end > b_start)


class TableBooking:
    def __init__(self, booking_file: str = BOOKING_FILE):
        os.makedirs(os.path.dirname(booking_file), exist_ok=True)
        self.booking_file = booking_file
        self.validation = Validation()
        self.logger = logger
        self._ensure_booking_file()

    
    def _ensure_booking_file(self):
        if not os.path.exists(self.booking_file):
            try:
                with open(self.booking_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
                self.logger.info("Created bookings.json")
            except Exception as e:
                self.logger.error(f"Failed creating bookings.json: {e}")

    def _load_bookings(self) -> List[Dict]:
        try:
            with open(self.booking_file, "r", encoding="utf-8") as f:
                data = json.load(f) or []
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_bookings(self, bookings: List[Dict]) -> bool:
        try:
            with open(self.booking_file, "w", encoding="utf-8") as f:
                json.dump(bookings, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save bookings.json: {e}")
            return False

    def _next_booking_id(self, bookings: List[Dict]) -> int:
        if not bookings:
            return 1
        return max(int(b.get("booking_id", 0)) for b in bookings) + 1

    # admin auth
    def _admin_authenticate(self) -> bool:
        try:
            print("Admin authentication required.")
            aid = input("Admin ID: ").strip()
            aemail = input("Admin Email: ").strip()
            apw = getpass.getpass("Admin Password: ").strip()
            if not (self.validation.is_valid_id(aid) and self.validation.non_empty(aemail)):
                print("Invalid admin credential format.")
                self.logger.warning("Admin provided invalid auth format.")
                return False
            if int(aid) == ADMIN["id"] and aemail.lower() == ADMIN["email"].lower() and apw == ADMIN["password"]:
                self.logger.info("Admin authenticated for table booking admin action.")
                return True
            print("Admin authentication failed.")
            self.logger.warning("Admin authentication failed.")
            return False
        except Exception as e:
            self.logger.error(f"Exception during admin auth: {e}")
            return False

    
    def _tables_needed(self, persons: int) -> int:
        return (persons + SEATS_PER_TABLE - 1) // SEATS_PER_TABLE

    def _occupied_tables_for_slot(self, booking_date: date, start_time: time, hours: int, exclude_booking_id: Optional[int] = None) -> Set[int]:
        occupied: Set[int] = set()
        bookings = self._load_bookings()
        req_start = datetime.combine(booking_date, start_time)
        req_end = req_start + timedelta(hours=hours)
        for b in bookings:
            try:
                if exclude_booking_id is not None and int(b.get("booking_id", -1)) == int(exclude_booking_id):
                    continue
                b_date = datetime.strptime(str(b.get("date", "")), "%Y-%m-%d").date()
                b_start_time = datetime.strptime(str(b.get("start_time", "")), "%H:%M").time()
                b_start = datetime.combine(b_date, b_start_time)
                b_end = b_start + timedelta(hours=int(b.get("hours", 1)))
                if _intervals_overlap(req_start, req_end, b_start, b_end):
                    for t in b.get("tables", []):
                        occupied.add(int(t))
            except Exception:
                continue
        return occupied

    def available_tables(self, booking_date: date, start_time: time, hours: int, exclude_booking_id: Optional[int] = None) -> List[int]:
        try:
            occupied = self._occupied_tables_for_slot(booking_date, start_time, hours, exclude_booking_id=exclude_booking_id)
            all_tables = set(range(1, NUM_TABLES + 1))
            free = sorted(list(all_tables - occupied))
            return free
        except Exception as e:
            self.logger.error(f"Error computing available tables: {e}")
            return []

    def show_tables_status(self, booking_date: date, start_time: time, hours: int, exclude_booking_id: Optional[int] = None):
        try:
            free = set(self.available_tables(booking_date, start_time, hours, exclude_booking_id=exclude_booking_id))
            print(f"\nTable statuses for {booking_date} at {start_time.strftime('%H:%M')} for {hours} hour(s):")
            for tid in range(1, NUM_TABLES + 1):
                status = "Available" if tid in free else "Booked"
                print(f"Table {tid:02d}: {status}")
            print()
        except Exception as e:
            self.logger.error(f"Error showing table statuses: {e}")

    #  booking flow
    def book_table(self):
        try:
            d_in = input("Booking date (YYYY-MM-DD): ").strip()
            booking_date = self.validation.parse_date(d_in) if hasattr(self.validation, "parse_date") else None
            if not booking_date:
                print("Invalid date format. Use YYYY-MM-DD.")
                return
            if not self.validation.is_today_or_future_within_limit(booking_date):
                print(f"Booking must be today or within next {MAX_ADVANCE_DAYS} days (no past dates).")
                return

            t_in = input("Start time (HH:MM, 24-hour) - bookings may START only between 10:00 and 18:00: ").strip()
            start_t = self.validation.parse_time(t_in) if hasattr(self.validation, "parse_time") else None
            if not start_t:
                print("Invalid time format. Use HH:MM.")
                return

            hours_in = input(f"How many hours to book ({MIN_HOURS}-{MAX_HOURS}): ").strip()
            if not self.validation.is_valid_hours(hours_in):
                print("Invalid hours input.")
                return
            hours = int(hours_in)

            # Enforce booking start window (10:00..18:00)
            if start_t < BOOKING_START_ALLOWED or start_t > BOOKING_START_LAST:
                print(f"Bookings may START only between {BOOKING_START_ALLOWED.strftime('%H:%M')} and {BOOKING_START_LAST.strftime('%H:%M')}.")
                return

            # Also ensure booking does not extend past restaurant close (22:00)
            dt_start = datetime.combine(booking_date, start_t)
            dt_end = dt_start + timedelta(hours=hours)
            if dt_end.time() > RESTAURANT_CLOSE:
                print(f"Booking would end at {dt_end.time().strftime('%H:%M')}, which is after restaurant closing at {RESTAURANT_CLOSE.strftime('%H:%M')}. Reduce hours or choose earlier start.")
                return

            persons_in = input("Number of persons: ").strip()
            if not self.validation.is_valid_person_count(persons_in):
                print("Invalid number of persons.")
                return
            persons = int(persons_in)
            needed_tables = self._tables_needed(persons)
            if needed_tables * SEATS_PER_TABLE > RESTAURANT_CAPACITY:
                print("Requested seating exceeds restaurant capacity.")
                return

            # Show statuses
            self.show_tables_status(booking_date, start_t, hours)

            free_tables = self.available_tables(booking_date, start_t, hours)
            if len(free_tables) < needed_tables:
                print(f"Not enough tables available. Needed {needed_tables}, Free {len(free_tables)}. Free tables: {free_tables}")
                return

            allocated = free_tables[:needed_tables]
            print(f"Allocating tables: {allocated}")

            customer_name = input("Customer name: ").strip()
            contact = input("Contact number (10 digits): ").strip()
            if not self.validation.is_valid_contact(contact):
                print("Invalid contact number.")
                return
            notes = input("Special notes (optional): ").strip()

            bookings = self._load_bookings()
            booking_id = self._next_booking_id(bookings)
            record = {
                "booking_id": booking_id,
                "date": booking_date.strftime("%Y-%m-%d"),
                "start_time": start_t.strftime("%H:%M"),
                "hours": hours,
                "tables": allocated,
                "persons": persons,
                "customer_name": customer_name,
                "contact": contact,
                "notes": notes,
                "created_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
                "order": None,
                "payment": None
            }
            bookings.append(record)
            if not self._save_bookings(bookings):
                print("Failed to persist booking.")
                return

            print(f"Booking confirmed. ID: {booking_id}. Date: {record['date']} Start: {record['start_time']} Tables: {allocated}")
            self.logger.info(f"Booking {booking_id} created for {customer_name} on {record['date']} {record['start_time']} tables {allocated}")

            # Show updated statuses
            print("\nUpdated table statuses after booking:")
            self.show_tables_status(booking_date, start_t, hours)

            # Offer to take order immediately
            take_now = input("Take order now for this booking? (y/N): ").strip().lower()
            if take_now == "y":
                self._take_order_for_booking(booking_id)

        except Exception as e:
            print("An error occurred during booking.")
            self.logger.error(f"book_table exception: {e}")

    def _take_order_for_booking(self, booking_id: int):
        try:
            if MenuOrder is None:
                subtotal_raw = input("Enter order subtotal amount: ").strip()
                try:
                    subtotal = float(subtotal_raw)
                except Exception:
                    print("Invalid amount.")
                    return
                gst = round(subtotal * 0.18, 2)
                final = round(subtotal + gst, 2)
                print(f"GST (18%): {gst:.2f} | Final total: {final:.2f}")
                payment = self._collect_payment(final)
                bookings = self._load_bookings()
                for b in bookings:
                    if int(b.get("booking_id", -1)) == booking_id:
                        b["order"] = {"subtotal": subtotal, "gst": gst, "final_total": final, "note": "manual entry"}
                        b["payment"] = payment
                        break
                self._save_bookings(bookings)
                self.logger.info(f"Manual order recorded for booking {booking_id}: total {final:.2f}")
                return

            mo = MenuOrder()
            if hasattr(mo, "take_order"):
                mo.take_order()
            elif hasattr(mo, "main"):
                mo.main()
            else:
                print("Menu module present but has no order entrypoint.")
                return

            orders_path = os.path.join(DB_DIR, "orders.json")
            if not os.path.exists(orders_path):
                print("Order log not found.")
                return
            with open(orders_path, "r", encoding="utf-8") as f:
                orders_list = json.load(f) or []
            if not orders_list:
                print("No recorded orders to attach.")
                return
            last_order = orders_list[-1]
            base_total = float(last_order.get("total", 0.0))
            gst = round(base_total * 0.18, 2)
            final_total = round(base_total + gst, 2)
            print(f"Order base {base_total:.2f}, GST {gst:.2f}, Final {final_total:.2f}")
            payment = self._collect_payment(final_total)
            bookings = self._load_bookings()
            for b in bookings:
                if int(b.get("booking_id", -1)) == booking_id:
                    b["order"] = {"menu_order_reference": last_order, "gst": gst, "final_total": final_total}
                    b["payment"] = payment
                    break
            self._save_bookings(bookings)
            self.logger.info(f"Order attached to booking {booking_id}: final {final_total:.2f}")
        except Exception as e:
            self.logger.error(f"_take_order_for_booking exception: {e}")

    def _collect_payment(self, amount: float) -> Dict:
        try:
            print("Payment methods: 1. Cash  2. Google Pay  3. Netbanking")
            ch = input("Choose (1/2/3): ").strip()
            method = {"1": "Cash", "2": "Google Pay", "3": "Netbanking"}.get(ch, "Cash")
            if method == "Cash":
                print(f"Collected cash: {amount:.2f}")
                return {"method": "Cash", "amount": round(amount, 2), "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds")}
            txn = input(f"Enter transaction/reference ID for {method}: ").strip()
            return {"method": method, "amount": round(amount, 2), "txn_id": txn, "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds")}
        except Exception as e:
            self.logger.error(f"_collect_payment exception: {e}")
            return {"method": "Unknown", "amount": round(amount, 2), "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds")}

    # listing / admin operations
    def list_bookings(self, for_date: Optional[date] = None):
        try:
            bookings = self._load_bookings()
            if for_date:
                bookings = [b for b in bookings if b.get("date") == for_date.strftime("%Y-%m-%d")]
            if not bookings:
                print("No bookings found.")
                return
            print("\nBookings:")
            for b in sorted(bookings, key=lambda x: (x.get("date", ""), x.get("start_time", ""))):
                print(f"ID:{b.get('booking_id')} | Date:{b.get('date')} | Start:{b.get('start_time')} | Hours:{b.get('hours')} | Tables:{b.get('tables')} | Persons:{b.get('persons')} | Name:{b.get('customer_name')}")
            print()
        except Exception as e:
            self.logger.error(f"list_bookings exception: {e}")

    def update_booking(self):
        if not self._admin_authenticate():
            return
        try:
            bookings = self._load_bookings()
            bid = input("Booking ID to update: ").strip()
            if not bid.isdigit():
                print("Invalid booking ID.")
                return
            bid_i = int(bid)
            booking = next((b for b in bookings if int(b.get("booking_id", -1)) == bid_i), None)
            if not booking:
                print("Booking not found.")
                return

            # -------------------------------------------------------------------
            new_date_in = input(f"Date [{booking['date']}]: ").strip() or booking['date']
            new_date = self.validation.parse_date(new_date_in)
            if not new_date:
                print("Invalid date.")
                return
            if not self.validation.is_today_or_future_within_limit(new_date):
                print("Date must be today or within next 90 days.")
                return

            new_time_in = input(f"Start time [{booking['start_time']}]: ").strip() or booking['start_time']
            new_time = self.validation.parse_time(new_time_in)
            if not new_time:
                print("Invalid time.")
                return

            new_hours_in = input(f"Hours [{booking['hours']}]: ").strip() or str(booking['hours'])
            if not self.validation.is_valid_hours(new_hours_in):
                print("Invalid hours.")
                return
            new_hours = int(new_hours_in)

            #  booking start window and closing check
            if new_time < BOOKING_START_ALLOWED or new_time > BOOKING_START_LAST:
                print(f"Bookings may START only between {BOOKING_START_ALLOWED.strftime('%H:%M')} and {BOOKING_START_LAST.strftime('%H:%M')}.")
                return
            dt_start = datetime.combine(new_date, new_time)
            dt_end = dt_start + timedelta(hours=new_hours)
            if dt_end.time() > RESTAURANT_CLOSE:
                print(f"Updated booking would end at {dt_end.time().strftime('%H:%M')}, after closing at {RESTAURANT_CLOSE.strftime('%H:%M')}.")
                return

            new_persons_in = input(f"Persons [{booking['persons']}]: ").strip() or str(booking['persons'])
            if not self.validation.is_valid_person_count(new_persons_in):
                print("Invalid persons.")
                return
            new_persons = int(new_persons_in)
            needed_tables = self._tables_needed(new_persons)

            # compute available excluding this booking
            free = self.available_tables(new_date, new_time, new_hours, exclude_booking_id=bid_i)
            if len(free) < needed_tables:
                print(f"Not enough tables available for new slot. Free: {free}")
                return

            allocated = free[:needed_tables]
            booking['date'] = new_date.strftime("%Y-%m-%d")
            booking['start_time'] = new_time.strftime("%H:%M")
            booking['hours'] = new_hours
            booking['persons'] = new_persons
            booking['tables'] = allocated
            booking['modified_at'] = datetime.now().isoformat(sep=" ", timespec="seconds")

            self._save_bookings(bookings)
            print(f"Booking {bid_i} updated. New tables: {allocated}")
            self.logger.info(f"Booking {bid_i} updated by admin. New tables: {allocated}")
        except Exception as e:
            print("Failed to update booking.")
            self.logger.error(f"update_booking exception: {e}")

    def delete_booking(self):
        if not self._admin_authenticate():
            return
        try:
            bookings = self._load_bookings()
            bid = input("Booking ID to delete: ").strip()
            if not bid.isdigit():
                print("Invalid booking ID.")
                return
            bid_i = int(bid)
            booking = next((b for b in bookings if int(b.get("booking_id", -1)) == bid_i), None)
            if not booking:
                print("Booking not found.")
                return
            confirm = input(f"Confirm delete booking {bid_i} on {booking['date']} {booking['start_time']}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return
            bookings = [b for b in bookings if int(b.get("booking_id", -1)) != bid_i]
            self._save_bookings(bookings)
            print("Booking deleted.")
            self.logger.info(f"Booking {bid_i} deleted by admin.")
        except Exception as e:
            print("Failed to delete booking.")
            self.logger.error(f"delete_booking exception: {e}")

    def show_available(self):
        try:
            d_in = input("Date to check (YYYY-MM-DD): ").strip()
            booking_date = self.validation.parse_date(d_in)
            if not booking_date:
                print("Invalid date.")
                return
            t_in = input("Start time (HH:MM): ").strip()
            start_t = self.validation.parse_time(t_in)
            if not start_t:
                print("Invalid time.")
                return
            hours_in = input(f"Hours ({MIN_HOURS}-{MAX_HOURS}): ").strip()
            if not self.validation.is_valid_hours(hours_in):
                print("Invalid hours.")
                return
            hours = int(hours_in)

            #  booking start allowed window and closing check
            if start_t < BOOKING_START_ALLOWED or start_t > BOOKING_START_LAST:
                print(f"Bookings may START only between {BOOKING_START_ALLOWED.strftime('%H:%M')} and {BOOKING_START_LAST.strftime('%H:%M')}.")
                return
            dt_start = datetime.combine(booking_date, start_t)
            dt_end = dt_start + timedelta(hours=hours)
            if dt_end.time() > RESTAURANT_CLOSE:
                print(f"Requested slot would end at {dt_end.time().strftime('%H:%M')}, after closing at {RESTAURANT_CLOSE.strftime('%H:%M')}.")
                return

            self.show_tables_status(booking_date, start_t, hours)
        except Exception as e:
            print("Failed to show availability.")
            self.logger.error(f"show_available exception: {e}")

    def main(self):
        try:
            while True:
                print("\nTABLE BOOKING MODULE")
                print("1. Book Table")
                print("2. Show Available Tables")
                print("3. List Bookings (all)")
                print("4. List Bookings (by date)")
                print("5. Admin - Update Booking")
                print("6. Admin - Delete Booking")
                print("7. Back/Exit")
                ch = input("Choose: ").strip()
                if ch == "1":
                    self.book_table()
                elif ch == "2":
                    self.show_available()
                elif ch == "3":
                    self.list_bookings()
                elif ch == "4":
                    d_in = input("Date (YYYY-MM-DD): ").strip()
                    d = self.validation.parse_date(d_in)
                    if not d:
                        print("Invalid date.")
                    else:
                        self.list_bookings(for_date=d)
                elif ch == "5":
                    self.update_booking()
                elif ch == "6":
                    self.delete_booking()
                elif ch == "7":
                    break
                else:
                    print("Invalid choice.")
        except Exception as e:
            self.logger.error(f"table_booking main loop exception: {e}")
            print("Table booking module encountered an error.")


if __name__ == "__main__":
    tb = TableBooking()
    try:
        tb.main()
    except KeyboardInterrupt:
        print("\nExiting table booking module.")
    except Exception as e:
        tb.logger.error(f"Fatal error in table_booking: {e}")
