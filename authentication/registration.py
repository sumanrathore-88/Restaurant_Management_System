# authentication/registration.py
"""
Registration module for staff management.

Features:
- Admin-only registration of staff (id, name, email, password, qualification, contact)
- Admin-only update / delete staff
- View staff list
- Simple interactive menu that lets you call into domain.menu_order and domain.table_booking
  (e.g., view menu, place order, book table, take order & pay)
- Uses domain.validation.load_users() and domain.validation.is_admin_credentials_valid()
  to read/check the same users JSON used elsewhere.
- Logs actions via domain.logs.log_event
"""

import json
import os
from getpass import getpass
from typing import Dict, Any

# Import domain modules (existing in your project)
from domain import validation, logs, menu_order, table_booking

# admin id per your spec
ADMIN_ID = "100"


def _ensure_db_folder():
    # ensure database folder exists - uses the same DB as validation module
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
    if not os.path.exists(db_path):
        os.makedirs(db_path, exist_ok=True)


def _load_users() -> Dict[str, Dict[str, Any]]:
    """
    Load users from database/users.json using validation.load_users (keeps single source).
    Returns dict keyed by user id (string).
    """
    return validation.load_users()


def _save_users(users: Dict[str, Dict[str, Any]]):
    """
    Save users back to database/users.json. We keep the same file used by validation.load_users.
    """
    _ensure_db_folder()
    users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "users.json")
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)


def _is_admin_authenticated() -> bool:
    """
    Prompt for admin password and verify using validation.is_admin_credentials_valid.
    """
    pwd = getpass("Enter admin password: ")
    valid = validation.is_admin_credentials_valid(ADMIN_ID, pwd)
    if not valid:
        logs.log_event("auth_failed", "Admin authentication failed during staff management", {"admin_id": ADMIN_ID})
    return valid


def _generate_staff_id(users: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate a new numeric staff id as string. Avoid collisions with existing user ids.
    If admin id 100 exists, keep generating > max existing id.
    """
    existing_ids = [int(i) for i in users.keys() if str(i).isdigit()]
    next_id = str(max(existing_ids) + 1 if existing_ids else 1)
    # ensure not reusing admin id
    if next_id == ADMIN_ID:
        next_id = str(int(next_id) + 1)
    return next_id


def register_staff():
    """
    Admin-only interactive staff registration.
    Staff fields: id (auto), name, email, password, qualification, contact
    """
    print("\n--- Register New Staff (Admin only) ---")
    if not _is_admin_authenticated():
        print("Authentication failed. Cannot register staff.")
        return False

    users = _load_users()

    # collect staff details
    name = input("Staff name: ").strip()
    email = input("Staff email: ").strip()
    password = getpass("Staff password: ").strip()
    qualification = input("Qualification: ").strip()
    contact = input("Contact number: ").strip()

    # basic sanity checks (kept simple here)
    if not name or not email or not password:
        print("Name, email and password are required. Aborting.")
        return False

    # generate id and save
    new_id = _generate_staff_id(users)
    users[new_id] = {
        "id": int(new_id),
        "name": name,
        "email": email,
        "password": password,
        "qualification": qualification,
        "contact": contact,
        "role": "staff"
    }
    _save_users(users)
    logs.log_event("staff_registered", f"Admin {ADMIN_ID} registered staff {name}", {"staff_id": new_id, "name": name, "email": email})
    print(f"Staff registered successfully with ID: {new_id}")
    return True


def update_staff():
    """
    Admin-only interactive update for an existing staff member.
    Admin can update name, email, password, qualification, contact.
    """
    print("\n--- Update Staff (Admin only) ---")
    if not _is_admin_authenticated():
        print("Authentication failed. Cannot update staff.")
        return False

    users = _load_users()
    staff_id = input("Enter staff ID to update: ").strip()
    if staff_id not in users:
        print("Staff ID not found.")
        return False

    staff = users[staff_id]
    print(f"Updating staff: {staff.get('name')} (ID {staff_id})")
    # show current values and prompt for new (press enter to keep)
    name = input(f"Name [{staff.get('name')}]: ").strip() or staff.get('name')
    email = input(f"Email [{staff.get('email')}]: ").strip() or staff.get('email')
    change_pwd = input("Change password? (y/N): ").strip().lower()
    if change_pwd == "y":
        password = getpass("New password: ").strip()
    else:
        password = staff.get("password")
    qualification = input(f"Qualification [{staff.get('qualification', '')}]: ").strip() or staff.get("qualification", "")
    contact = input(f"Contact [{staff.get('contact', '')}]: ").strip() or staff.get("contact", "")

    # apply changes
    users[staff_id].update({
        "name": name,
        "email": email,
        "password": password,
        "qualification": qualification,
        "contact": contact
    })
    _save_users(users)
    logs.log_event("staff_updated", f"Admin {ADMIN_ID} updated staff {staff_id}", {"staff_id": staff_id})
    print("Staff updated successfully.")
    return True


def delete_staff():
    """
    Admin-only deletion of a staff record.
    """
    print("\n--- Delete Staff (Admin only) ---")
    if not _is_admin_authenticated():
        print("Authentication failed. Cannot delete staff.")
        return False

    users = _load_users()
    staff_id = input("Enter staff ID to delete: ").strip()
    if staff_id not in users:
        print("Staff ID not found.")
        return False

    # prevent deleting admin accidentally
    if staff_id == ADMIN_ID:
        print("Cannot delete admin user.")
        return False

    staff_name = users[staff_id].get("name")
    confirm = input(f"Confirm deletion of {staff_name} (ID {staff_id})? (y/N): ").strip().lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return False

    users.pop(staff_id)
    _save_users(users)
    logs.log_event("staff_deleted", f"Admin {ADMIN_ID} deleted staff {staff_name}", {"staff_id": staff_id, "name": staff_name})
    print("Staff deleted successfully.")
    return True


def list_staff():
    """
    List all users (admin + staff). Shows id, name, email, qualification, contact, role.
    """
    print("\n--- Staff & Users ---")
    users = _load_users()
    if not users:
        print("No users found.")
        return
    print(f"{'ID':<6} {'Name':<20} {'Email':<25} {'Qualification':<15} {'Contact':<12} {'Role':<8}")
    print("-" * 90)
    for uid, info in sorted(users.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        print(f"{str(info.get('id', uid)):<6} {info.get('name','')[:20]:<20} {info.get('email','')[:25]:<25} {info.get('qualification','')[:15]:<15} {info.get('contact','')[:12]:<12} {info.get('role',''):<8}")


def registration_cli_menu():
    """
    Interactive menu for registration and also to call menu_order / table_booking functions.
    """
    while True:
        print("\n=== Registration / Staff Management ===")
        print("1. Register new staff (admin only)")
        print("2. Update staff (admin only)")
        print("3. Delete staff (admin only)")
        print("4. List staff/users")
        print("5. View Menu (calls domain.menu_order.display_menu)")
        print("6. Place Order (calls domain.menu_order.place_order) [staff]")
        print("7. Book Table (calls domain.table_booking.book_table) [customer]")
        print("8. Take Order & Pay (calls domain.table_booking.take_order_and_pay) [staff]")
        print("9. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_staff()
        elif choice == "2":
            update_staff()
        elif choice == "3":
            delete_staff()
        elif choice == "4":
            list_staff()
        elif choice == "5":
            # call menu display from menu_order
            menu_order.display_menu()
        elif choice == "6":
            staff_name = input("Enter staff name placing the order: ").strip()
            if not staff_name:
                print("Staff name required.")
            else:
                menu_order.place_order(staff_name)
        elif choice == "7":
            table_booking.book_table()
        elif choice == "8":
            staff_name = input("Enter staff name: ").strip()
            t = input("Table number (or press enter for walk-in): ").strip()
            table_no = int(t) if t else None
            table_booking.take_order_and_pay(staff_name, table_no)
        elif choice == "9":
            print("Exiting registration menu.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Ensure DB exists and then start CLI
    _ensure_db_folder()
    print("Starting Registration CLI. Admin id is '100' per system config.")
    registration_cli_menu()
