import os
import json
from getpass import getpass
from pathlib import Path
from domain.validation import validate_email, validate_contact, validate_nonempty, is_admin
from domain.menu_order import Menu, OrderManager
from domain.table_booking import TableBooking
from domain.logs import setup_logger

DB_DIR = Path(__file__).parents[1] / 'database'
DB_DIR.mkdir(exist_ok=True)
STAFF_FILE = DB_DIR / 'staff.json'

logger = setup_logger()


class Staff:
    def __init__(self, staff_id: int, name: str, email: str, password: str, contact: str, qualification: str):
        self.staff_id = int(staff_id)
        self.name = name
        self.email = email
        self.password = password
        self.contact = contact
        self.qualification = qualification

    def to_dict(self):
        return self.__dict__


def load_staff():
    if not STAFF_FILE.exists():
        # create admin pre-seeded
        admin = {
            "100": {
                "staff_id": 100,
                "name": "suman rathore",
                "email": "suman@gmail.com",
                "password": "suman123",
                "contact": "",
                "qualification": "admin"
            }
        }
        STAFF_FILE.write_text(json.dumps(admin, indent=2))
        return admin
    return json.loads(STAFF_FILE.read_text())


def save_staff(data: dict):
    STAFF_FILE.write_text(json.dumps(data, indent=2))


def register_staff():
    staff_db = load_staff()
    print('\n--- Staff Registration ---')
    while True:
        try:
            staff_id = int(input('Enter staff ID (numeric): ').strip())
        except ValueError:
            print('Invalid ID — must be numeric.')
            continue
        if str(staff_id) in staff_db:
            print('Staff ID already exists. Choose another.')
            continue
        break

    name = input('Name: ').strip()
    email = input('Email: ').strip()
    password = getpass('Password: ')
    contact = input('Contact (digits): ').strip()
    qualification = input('Qualification: ').strip()

    # validations
    if not validate_nonempty(name):
        print('Name cannot be empty')
        return
    if not validate_email(email):
        print('Invalid email')
        return
    if not validate_contact(contact):
        print('Invalid contact')
        return

    staff = Staff(staff_id, name, email, password, contact, qualification)
    staff_db[str(staff_id)] = staff.to_dict()
    save_staff(staff_db)
    logger.info(f'New staff registered: {staff_id} - {name}')
    print(f'Staff {name} registered successfully.')


def staff_login():
    staff_db = load_staff()
    print('\n--- Staff Login ---')
    sid = input('Staff ID: ').strip()
    pwd = getpass('Password: ')
    if sid not in staff_db:
        print('No such staff ID.')
        return None
    rec = staff_db[sid]
    if rec['password'] != pwd:
        print('Incorrect password')
        return None
    print(f"Welcome {rec['name']}")
    logger.info(f'Staff logged in: {sid} - {rec["name"]}')
    return int(sid)


def staff_menu_loop(staff_id: int):
    menu = Menu()
    orders = OrderManager()
    bookings = TableBooking()

    while True:
        print('\n-- Actions --')
        print('1. View Menu')
        print('2. Take Order')
        print('3. Book Table')
        print('4. View Bookings')
        print('5. Logout')
        if is_admin(staff_id):
            print('6. Admin: Modify Menu (admin only)')
        choice = input('Choose: ').strip()

        if choice == '1':
            menu.display_menu()
        elif choice == '2':
            orders.create_order(staff_id)
        elif choice == '3':
            bookings.book_table()
        elif choice == '4':
            bookings.view_bookings()
        elif choice == '5':
            print('Logging out...')
            break
        elif choice == '6' and is_admin(staff_id):
            menu.admin_modify_menu()
        else:
            print('Invalid option')


if __name__ == '__main__':
    print('Run main.py to start the application')
