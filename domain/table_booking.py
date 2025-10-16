
import json
from pathlib import Path
from datetime import datetime
from domain.menu_order import Menu, OrderManager
from domain.logs import setup_logger

DB_DIR = Path(__file__).parents[1] / 'database'
DB_DIR.mkdir(exist_ok=True)
BOOK_FILE = DB_DIR / 'bookings.json'

logger = setup_logger()


class TableBooking:
    def __init__(self):
        if not BOOK_FILE.exists():
            BOOK_FILE.write_text(json.dumps({}, indent=2))
        self.bookings = json.loads(BOOK_FILE.read_text())
        self.menu = Menu()
        self.orders = OrderManager()

    def save(self):
        BOOK_FILE.write_text(json.dumps(self.bookings, indent=2))

    def book_table(self):
        print('\n--- Table Booking ---')
        name = input('Customer name: ').strip()
        contact = input('Contact: ').strip()
        pax = int(input('Number of people: ').strip() or 1)
        datetime_str = input('Booking datetime (YYYY-MM-DD HH:MM) or leave blank for now: ').strip()
        if not datetime_str:
            dt = datetime.utcnow().isoformat()
        else:
            try:
                dt = datetime.fromisoformat(datetime_str).isoformat()
            except Exception:
                dt = datetime.utcnow().isoformat()

        bid = str(int(datetime.utcnow().timestamp() * 1000))
        self.bookings[bid] = {
            'customer': name,
            'contact': contact,
            'pax': pax,
            'datetime': dt,
            'order_id': None
        }
        self.save()
        logger.info(f'New booking {bid} for {name} at {dt}')
        print(f'Booking created. ID: {bid}')
        # Ask if they want to order now
        choose = input('Take order now for this booking? (y/n): ').strip().lower()
        if choose == 'y':
            # create order and attach
            self.orders.create_order(staff_id=0)
            # find last order id
            last_oid = max(self.orders.orders.keys(), key=lambda x: x)
            self.bookings[bid]['order_id'] = last_oid
            self.save()
            print('Order attached to booking.')

    def view_bookings(self):
        print('\n--- Current Bookings ---')
        if not self.bookings:
            print('No bookings')
            return
        for k, v in self.bookings.items():
            print(f"ID: {k} | Customer: {v['customer']} | pax: {v['pax']} | datetime: {v['datetime']} | order: {v.get('order_id')}")


if __name__ == '__main__':
    b = TableBooking()
    b.book_table()

