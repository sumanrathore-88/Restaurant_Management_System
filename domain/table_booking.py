
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any


try:
    from domain.validation import Validation
except Exception:
    class Validation:
        @staticmethod
        def validate_table_number(n):
            if not isinstance(n, int) or not (1 <= n <= 20):
                raise ValueError("Table number must be integer between 1 and 20.")
        @staticmethod
        def validate_name(name):
            if not isinstance(name, str) or len(name.strip()) < 2:
                raise ValueError("Name must be at least 2 characters long.")
        @staticmethod
        def validate_contact(contact):
            if not isinstance(contact, str) or not contact.strip().isdigit():
                raise ValueError("Contact must be digits only.")
        @staticmethod
        def validate_num_people(n):
            if not isinstance(n, int) or n <= 0 or n > 20:
                raise ValueError("Number of people must be 1..20.")
        @staticmethod
        def validate_datetime(dt):
            if not isinstance(dt, datetime):
                raise ValueError("Invalid datetime object.")

try:
    from domain.logs import Logger
except Exception:
    import sys
    class Logger:
        @staticmethod
        def info(msg): print(f"[INFO] {msg}")
        @staticmethod
        def warn(msg): print(f"[WARN] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}", file=sys.stderr)
        @staticmethod
        def exception(e): print(f"[EXCEPTION] {e}", file=sys.stderr)


DB_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "database"))
BOOKINGS_FILE = os.path.join(DB_DIR, "bookings.json")
os.makedirs(os.path.dirname(BOOKINGS_FILE), exist_ok=True)

class BookingError(Exception):
    pass

class Booking:
    def __init__(self, booking_id:int, table_no:int, customer_name:str, contact:str,
                 num_people:int, booking_for:datetime, booked_by:str, created_at:Optional[datetime]=None):
        Validation.validate_table_number(table_no)
        Validation.validate_name(customer_name)
        Validation.validate_contact(contact)
        Validation.validate_num_people(num_people)
        Validation.validate_datetime(booking_for)

        self.booking_id = int(booking_id)
        self.table_no = int(table_no)
        self.customer_name = customer_name.strip()
        self.contact = contact.strip()
        self.num_people = int(num_people)
        self.booking_for = booking_for
        self.booked_by = booked_by
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "booking_id": self.booking_id,
            "table_no": self.table_no,
            "customer_name": self.customer_name,
            "contact": self.contact,
            "num_people": self.num_people,
            "booking_for": self.booking_for.strftime("%Y-%m-%d %H:%M"),
            "booked_by": self.booked_by,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        bf = datetime.strptime(d["booking_for"], "%Y-%m-%d %H:%M")
        ca = datetime.strptime(d["created_at"], "%Y-%m-%d %H:%M:%S")
        return Booking(
            booking_id=int(d["booking_id"]),
            table_no=int(d["table_no"]),
            customer_name=d["customer_name"],
            contact=d["contact"],
            num_people=int(d["num_people"]),
            booking_for=bf,
            booked_by=d.get("booked_by", "Staff"),
            created_at=ca
        )

class TableBooking:
    def __init__(self, bookings_file: str = BOOKINGS_FILE):
        self.bookings_file = bookings_file
        if not os.path.exists(self.bookings_file):
            try:
                with open(self.bookings_file, "w", encoding="utf-8") as f:
                    json.dump({"bookings": []}, f, indent=2)
            except OSError as e:
                Logger.error(f"Could not create bookings DB: {e}")
                raise BookingError(e)
        self.last_booking_table_no: Optional[int] = None

    def _read_all(self):
        try:
            with open(self.bookings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise BookingError("Bookings DB corrupted.")
        except OSError as e:
            raise BookingError(e)

    def _write_all(self, data):
        try:
            with open(self.bookings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            raise BookingError(e)

    def list_bookings(self):
        data = self._read_all()
        return [Booking.from_dict(d) for d in data.get("bookings", [])]

    def find_conflict(self, table_no:int, booking_for:datetime):
        for b in self.list_bookings():
            if b.table_no == table_no and b.booking_for == booking_for:
                return b
        return None

    def add_booking(self, booking: Booking):
        data = self._read_all()
        bookings = data.get("bookings", [])
        if any(int(b.get("booking_id")) == booking.booking_id for b in bookings):
            raise BookingError("Booking ID already exists.")
        conflict = self.find_conflict(booking.table_no, booking.booking_for)
        if conflict:
            raise BookingError(f"Table {booking.table_no} already booked at {booking.booking_for}.")
        bookings.append(booking.to_dict())
        data["bookings"] = bookings
        self._write_all(data)
        self.last_booking_table_no = booking.table_no
        Logger.info(f"Booking added: id={booking.booking_id}, table={booking.table_no}, for={booking.booking_for}")
        return booking

    def cancel_booking(self, booking_id:int):
        data = self._read_all()
        bookings = data.get("bookings", [])
        new = [b for b in bookings if int(b.get("booking_id", -1)) != int(booking_id)]
        if len(new) == len(bookings):
            raise BookingError(f"No booking with ID {booking_id}.")
        data["bookings"] = new
        self._write_all(data)
        Logger.info(f"Cancelled booking {booking_id}")

    
    def book_table_interactive(self):
        print("=== Table Booking (staff) ===")
        try:
            staff_name = input("Staff name: ").strip() or "Staff"
            customer_name = input("Customer name: ").strip()
            contact = input("Customer contact (digits only): ").strip()
            num_people_raw = input("Number of people: ").strip()
            table_raw = input("Table number (1-20): ").strip()
            dt_input = input("Booking date & time (YYYY-MM-DD HH:MM) or 'now': ").strip()

            if not num_people_raw.isdigit():
                print("Number of people must be numeric.")
                return None
            num_people = int(num_people_raw)

            if not table_raw.isdigit():
                print("Table number must be numeric.")
                return None
            table_no = int(table_raw)

            if dt_input.lower() == "now":
                booking_for = datetime.now().replace(second=0, microsecond=0)
            else:
                try:
                    booking_for = datetime.strptime(dt_input, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid datetime format. Use YYYY-MM-DD HH:MM or 'now'.")
                    return None

            
            Validation.validate_name(customer_name)
            Validation.validate_contact(contact)
            Validation.validate_num_people(num_people)
            Validation.validate_table_number(table_no)
            Validation.validate_datetime(booking_for)

            
            conflict = self.find_conflict(table_no, booking_for)
            if conflict:
                print(f"Conflict: table {table_no} already booked at {booking_for.strftime('%Y-%m-%d %H:%M')}.")
                return None

            booking_id = int(datetime.now().timestamp() * 1000) % 1000000000
            booking = Booking(
                booking_id=booking_id,
                table_no=table_no,
                customer_name=customer_name,
                contact=contact,
                num_people=num_people,
                booking_for=booking_for,
                booked_by=staff_name
            )
            self.add_booking(booking)
            print(f"Booking confirmed: ID {booking.booking_id} | Table {booking.table_no} | For {booking.booking_for.strftime('%Y-%m-%d %H:%M')}")
        except (ValueError, BookingError) as e:
            print(f"Failed to create booking: {e}")
            Logger.warn(f"Booking failed: {e}")
            return None
        except Exception as e:
            Logger.exception(e)
            return None

        # --- AFTER SUCCESSFUL BOOKING: TAKE ORDER & BILL ---
        
        try:
            from domain.menu_order import Menu
        except Exception as e:
            Logger.warn(f"Menu module not available: {e}")
            print("Menu/order module not available or does not expose take_order_interactive. Order skipped.")
            return booking

        
        try:
            menu = Menu()
            
            try:
                
                order = menu.take_order_interactive()
            except TypeError:
                order = menu.take_order_interactive()
        except Exception as e:
            Logger.warn(f"Taking order failed after booking: {e}")
            print(f"Failed to take order after booking: {e}")
            return booking

        
        try:
            if order is not None and hasattr(order, "table_no"):
                if not getattr(order, "table_no"):
                    setattr(order, "table_no", booking.table_no)
                Logger.info(f"Order taken for booking id={booking.booking_id} table={booking.table_no}")
        except Exception:
            
            pass

        return booking
