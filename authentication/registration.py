
import json
import os
import sys
from getpass import getpass
from typing import List, Dict, Any

# --- Admin credentials (as requested) ---
ADMIN = {
    "name": "suman rathore",
    "id": 100,
    "email": "suman@gmail.com",
    "password": "suman123",
}

# Determine database file path relative to this file (../database/staffs.json)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "database"))
DB_PATH = os.path.join(DB_DIR, "staffs.json")

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)


def load_staffs() -> List[Dict[str, Any]]:
    """Load staff list from the JSON database file. Returns empty list if file missing or invalid."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except Exception:
        return []


def save_staffs(staffs: List[Dict[str, Any]]) -> None:
    """Save staff list to the JSON database file."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(staffs, f, indent=4)


def authenticate_admin() -> bool:
    """Prompt for admin email and password and authenticate against ADMIN credentials."""
    print("--- Admin Authentication Required ---")
    email = input("Admin email: ").strip()
    password = getpass("Admin password: ")

    if email == ADMIN["email"] and password == ADMIN["password"]:
        print("Authentication successful. Welcome, {}!".format(ADMIN["name"]))
        return True
    else:
        print("Authentication failed. Access denied.")
        return False


def find_staff_by_id(staffs: List[Dict[str, Any]], staff_id: str) -> int:
    """Return index of staff with given id (string) or -1 if not found."""
    for i, s in enumerate(staffs):
        if str(s.get("id")) == str(staff_id):
            return i
    return -1


def view_staffs(staffs: List[Dict[str, Any]]) -> None:
    """Print all staff records."""
    if not staffs:
        print("No staff records found.")
        return

    print("--- Staff List (all fields) ---")
    print(f"Total: {len(staffs)}")
    print("-" * 60)
    for s in staffs:
        print(f"ID          : {s.get('id')}")
        print(f"Name        : {s.get('name')}")
        print(f"Email       : {s.get('email')}")
        print(f"Password    : {s.get('password')}")
        print(f"Contact     : {s.get('contact')}")
        print(f"Qualification: {s.get('qualification')}")
        print("-" * 60)


def add_staff(staffs: List[Dict[str, Any]]) -> None:
    """Add a new staff record. Prevent duplicate IDs or emails."""
    print("--- Add New Staff ---")
    staff_id = input("ID: ").strip()
    if find_staff_by_id(staffs, staff_id) != -1:
        print("A staff member with this ID already exists. Aborting add.")
        return

    name = input("Name: ").strip()
    email = input("Email: ").strip()
    # check duplicate email
    if any(str(s.get("email", "")).lower() == email.lower() for s in staffs):
        print("A staff member with this email already exists. Aborting add.")
        return

    password = getpass("Password (input hidden): ")
    contact = input("Contact: ").strip()
    qualification = input("Qualification: ").strip()

    new_staff = {
        "id": staff_id,
        "name": name,
        "email": email,
        "password": password,
        "contact": contact,
        "qualification": qualification,
    }
    staffs.append(new_staff)
    save_staffs(staffs)
    print("Staff added successfully.")


def update_staff(staffs: List[Dict[str, Any]]) -> None:
    """Update an existing staff record by ID."""
    print("--- Update Staff ---")
    staff_id = input("Enter ID of staff to update: ").strip()
    idx = find_staff_by_id(staffs, staff_id)
    if idx == -1:
        print("Staff with this ID not found.")
        return

    staff = staffs[idx]
    print("Leave field empty to keep current value.")
    print(f"Current name: {staff.get('name')}")
    name = input("New name: ").strip()
    if name:
        staff["name"] = name

    print(f"Current email: {staff.get('email')}")
    email = input("New email: ").strip()
    if email:
        # ensure email not used by another staff
        if any(i != idx and str(s.get("email", "")).lower() == email.lower() for i, s in enumerate(staffs)):
            print("Another staff uses this email. Email not updated.")
        else:
            staff["email"] = email

    change_pw = input("Change password? (y/N): ").strip().lower()
    if change_pw == "y":
        pw = getpass("New password (input hidden): ")
        if pw:
            staff["password"] = pw

    print(f"Current contact: {staff.get('contact')}")
    contact = input("New contact: ").strip()
    if contact:
        staff["contact"] = contact

    print(f"Current qualification: {staff.get('qualification')}")
    qualification = input("New qualification: ").strip()
    if qualification:
        staff["qualification"] = qualification

    staffs[idx] = staff
    save_staffs(staffs)
    print("Staff updated successfully.")


def delete_staff(staffs: List[Dict[str, Any]]) -> None:
    """Delete staff by ID after confirmation."""
    print("--- Delete Staff ---")
    staff_id = input("Enter ID of staff to delete: ").strip()
    idx = find_staff_by_id(staffs, staff_id)
    if idx == -1:
        print("Staff with this ID not found.")
        return

    staff = staffs[idx]
    print("You are about to delete the following staff:")
    print(f"ID: {staff.get('id')}, Name: {staff.get('name')}, Email: {staff.get('email')}")
    confirm = input("Type DELETE to confirm: ")
    if confirm == "DELETE":
        staffs.pop(idx)
        save_staffs(staffs)
        print("Staff deleted.")
    else:
        print("Delete aborted.")


def show_menu() -> None:
    """Display the admin menu and handle choices.

    This function is intended to be called from main.py. It performs admin
    authentication once at the start; after successful login it will allow
    viewing, adding, updating and deleting staff records.
    """
    staffs = load_staffs()

    if not authenticate_admin():
        return

    while True:
        print("--- Admin: Staff Registration Management ---")
        print("1. View all staff records")
        print("2. Add staff")
        print("3. Update staff")
        print("4. Delete staff")
        print("5. Exit to main application")

        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            view_staffs(staffs)
        elif choice == "2":
            add_staff(staffs)
            staffs = load_staffs()
        elif choice == "3":
            update_staff(staffs)
            staffs = load_staffs()
        elif choice == "4":
            delete_staff(staffs)
            staffs = load_staffs()
        elif choice == "5":
            print("Returning to main application.")
            break
        else:
            print("Invalid choice. Try again.")

