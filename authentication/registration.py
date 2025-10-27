

import json
import os
from dataclasses import dataclass, asdict
from getpass import getpass
from typing import List, Optional, Dict


try:
    from domain.validation import Validation
except Exception:
    class Validation:
        @staticmethod
        def validate_id(v):
            if not str(v).isdigit() or int(v) <= 0:
                raise ValueError("ID must be positive integer.")
        @staticmethod
        def validate_name(n):
            if not n.strip():
                raise ValueError("Name required.")
        @staticmethod
        def validate_email(e):
            if "@" not in e:
                raise ValueError("Invalid email.")
        @staticmethod
        def validate_password(p):
            if len(p) < 4:
                raise ValueError("Password too short.")
        @staticmethod
        def validate_contact(c):
            if not c.strip().isdigit():
                raise ValueError("Contact must be numeric.")
        @staticmethod
        def validate_qualification(q):
            if not q.strip():
                raise ValueError("Qualification required.")

try:
    from domain.logs import Logger
except Exception:
    class Logger:
        @staticmethod
        def info(m): print(f"[INFO] {m}")
        @staticmethod
        def warn(m): print(f"[WARN] {m}")
        @staticmethod
        def error(m): print(f"[ERROR] {m}")

try:
    from domain.menu_order import Menu
except Exception:
    Menu = None
    Logger.warn("menu_order module not found — ordering disabled.")

# --- Database path ---
DB_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "database"))
STAFF_DB = os.path.join(DB_DIR, "staff.json")
os.makedirs(DB_DIR, exist_ok=True)

# --- Classes ---
@dataclass
class Staff:
    id: int
    name: str
    email: str
    password: str
    contact: str
    qualification: str

    def to_dict(self):
        return asdict(self)

class Admin:
    ADMIN_ID = 100
    ADMIN_NAME = "suman rathore"
    ADMIN_EMAIL = "suman@gmail.com"
    ADMIN_PASSWORD = "suman123"

    @classmethod
    def authenticate(cls, admin_id: int, password: str) -> bool:
        return admin_id == cls.ADMIN_ID and password == cls.ADMIN_PASSWORD

    @classmethod
    def authenticate_interactive(cls) -> bool:
        try:
            admin_id = input("Enter Admin ID: ").strip()
            if not admin_id.isdigit():
                print("Admin ID must be a number.")
                return False
            pwd = getpass("Enter Admin Password: ")
            if cls.authenticate(int(admin_id), pwd):
                print("Admin login successful.")
                Logger.info("Admin authenticated.")
                return True
            else:
                print("Invalid admin credentials.")
                return False
        except Exception as e:
            Logger.error(f"Admin login error: {e}")
            return False

class StaffDatabase:
    def __init__(self, file_path=STAFF_DB):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"staff": []}, f, indent=2)

    def _read(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, staff: Staff):
        data = self._read()
        for s in data["staff"]:
            if int(s["id"]) == staff.id or s["email"].lower() == staff.email.lower():
                raise ValueError("Staff with same ID or email already exists.")
        data["staff"].append(staff.to_dict())
        self._write(data)

    def find_by_id(self, staff_id: int):
        data = self._read()
        for s in data["staff"]:
            if int(s["id"]) == staff_id:
                return Staff(**s)
        return None

    def find_by_email(self, email: str):
        data = self._read()
        for s in data["staff"]:
            if s["email"].lower() == email.lower():
                return Staff(**s)
        return None


def register_staff_interactive():
    db = StaffDatabase()
    if not Admin.authenticate_interactive():
        return
    try:
        staff_id = int(input("Enter Staff ID: "))
        name = input("Enter Staff Name: ").strip()
        email = input("Enter Staff Email: ").strip()
        password = getpass("Enter Staff Password: ")
        confirm = getpass("Confirm Password: ")
        if password != confirm:
            print("Passwords do not match.")
            return
        contact = input("Enter Contact Number: ").strip()
        qualification = input("Enter Qualification: ").strip()

        # Validation
        Validation.validate_id(staff_id)
        Validation.validate_name(name)
        Validation.validate_email(email)
        Validation.validate_password(password)
        Validation.validate_contact(contact)
        Validation.validate_qualification(qualification)

        staff = Staff(staff_id, name, email, password, contact, qualification)
        db.add(staff)
        print(f"✅ Staff '{name}' (ID {staff_id}) registered successfully.")
        Logger.info(f"New staff added: {name}")
    except Exception as e:
        print(f"Registration failed: {e}")
        Logger.error(f"Registration failed: {e}")

def staff_sign_in_flow():
    db = StaffDatabase()
    print("\n== Staff Sign In ==")
    user = input("Enter Staff ID or Email: ").strip()
    password = getpass("Enter Password: ")

    # Admin login
    if user.isdigit() and int(user) == Admin.ADMIN_ID:
        if Admin.authenticate(int(user), password):
            print("Welcome Admin!")
            admin_console()
            return
        else:
            print("Invalid admin credentials.")
            return

    # Staff login
    staff = db.find_by_id(int(user)) if user.isdigit() else db.find_by_email(user)
    if not staff:
        print("No staff found.")
        return
    if staff.password != password:
        print("Incorrect password.")
        return

    print(f"Welcome, {staff.name}!")
    if Menu:
        try:
            Menu().take_order_interactive()
        except Exception as e:
            print(f"Menu system error: {e}")
    else:
        print("Menu module not available.")

def admin_console():
    while True:
        print("\n== ADMIN CONSOLE ==")
        print("1. Register new staff")
        print("2. View all staff")
        print("3. Back to Main Menu")
        choice = input("Enter choice (1-3): ").strip()
        db = StaffDatabase()

        if choice == "1":
            register_staff_interactive()
        elif choice == "2":
            data = db._read()
            if not data["staff"]:
                print("No staff found.")
            else:
                print("\nStaff List:")
                for s in data["staff"]:
                    print(f"ID:{s['id']} | Name:{s['name']} | Email:{s['email']} | Contact:{s['contact']}")
        elif choice == "3":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    while True:
        print("\n=== CHATORA AUTHENTICATION ===")
        print("1. Sign In")
        print("2. Sign Up (Register Staff)")
        print("3. Exit")
        ch = input("Enter choice (1-3): ").strip()
        if ch == "1":
            staff_sign_in_flow()
        elif ch == "2":
            register_staff_interactive()
        elif ch == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")
