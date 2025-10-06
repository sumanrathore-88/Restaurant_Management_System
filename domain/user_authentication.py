import json
import os
import getpass


# Get current directory (domain)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# JSON file path (inside ../database/)
JSON_FILE = os.path.join(BASE_DIR, "..", "database", "authentication.json")

# Default admin credentials
DEFAULT_ADMIN = {
    "id": 100,
    "name": "Suman Rathore",
    "email": "suman@gmail.com",
    "password": "suman123"
}


def load_data():
    
    json_path = os.path.abspath(JSON_FILE)
    if not os.path.exists(json_path):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        data = {"admin": DEFAULT_ADMIN, "staff": []}
        save_data(data)
        return data
    with open(json_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            data = {"admin": DEFAULT_ADMIN, "staff": []}
            save_data(data)
            return data

def save_data(data):
    """Save data to JSON file."""
    json_path = os.path.abspath(JSON_FILE)
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

def admin_authenticate(data):
    """Verify admin credentials."""
    print("\n--- Admin Authentication Required ---")
    try:
        admin_id_input = int(input("Enter admin id: ").strip())
    except ValueError:
        print("Invalid id (must be number).")
        return False
    admin_pass = getpass.getpass("Enter admin password: ")
    admin = data.get("admin", {})
    if admin_id_input == admin.get("id") and admin_pass == admin.get("password"):
        print("Admin authentication successful.\n")
        return True
    else:
        print("Admin authentication failed.\n")
        return False

# ---------------------------
# Staff Operations
# ---------------------------

def add_staff(data):
    print("\n--- Add Staff ---")
    if not admin_authenticate(data):
        return
    staff = data.get("staff", [])
    try:
        user_id = int(input("Enter staff id (number): ").strip())
    except ValueError:
        print("Invalid id (must be a number).")
        return
    if any(s["id"] == user_id for s in staff):
        print(f"Staff with id {user_id} already exists.")
        return
    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip()
    password = getpass.getpass("Enter password for staff: ")
    qualification = input("Enter qualification: ").strip()
    contact = input("Enter contact number: ").strip()

    new_staff = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": password,
        "qualification": qualification,
        "contact": contact
    }
    staff.append(new_staff)
    data["staff"] = staff
    save_data(data)
    print(f"Staff {name} (id={user_id}) added successfully.\n")

def search_staff(data):
    print("\n--- Search Staff ---")
    staff = data.get("staff", [])
    if not staff:
        print("No staff records found.\n")
        return

    print("Search by:\n 1 - ID\n 2 - Email\n 3 - Password")
    choice = input("Choose option (1/2/3): ").strip()
    if choice == "1":
        try:
            user_id = int(input("Enter staff id to search: ").strip())
        except ValueError:
            print("Invalid id (must be a number).")
            return
        found = [s for s in staff if s["id"] == user_id]
    elif choice == "2":
        email = input("Enter staff email to search: ").strip()
        found = [s for s in staff if s["email"].lower() == email.lower()]
    elif choice == "3":
        pwd = getpass.getpass("Enter staff password to search: ")
        found = [s for s in staff if s["password"] == pwd]
    else:
        print("Invalid choice.")
        return

    if not found:
        print("No matching staff found.\n")
    else:
        print(f"\nFound {len(found)} record(s):")
        for s in found:
            print_staff_record(s)
        print("")

def print_staff_record(s):
    print(f"ID: {s['id']}")
    print(f"Name: {s['name']}")
    print(f"Email: {s['email']}")
    print(f"Password: {s['password']}")
    print(f"Qualification: {s['qualification']}")
    print(f"Contact: {s['contact']}")
    print("-" * 30)

def update_staff(data):
    print("\n--- Update Staff ---")
    if not admin_authenticate(data):
        return
    staff = data.get("staff", [])
    if not staff:
        print("No staff records to update.\n")
        return
    try:
        user_id = int(input("Enter staff id to update: ").strip())
    except ValueError:
        print("Invalid id (must be a number).")
        return
    for idx, s in enumerate(staff):
        if s["id"] == user_id:
            print("\nCurrent information:")
            print_staff_record(s)
            print("Leave input blank to keep current value.")
            new_name = input(f"New name [{s['name']}]: ").strip()
            new_email = input(f"New email [{s['email']}]: ").strip()
            change_pass = input("Change password? (y/N): ").strip().lower()
            if change_pass == "y":
                new_password = getpass.getpass("Enter new password: ")
            else:
                new_password = s["password"]
            new_qualification = input(f"New qualification [{s['qualification']}]: ").strip()
            new_contact = input(f"New contact [{s['contact']}]: ").strip()

            # Apply updates
            if new_name:
                s["name"] = new_name
            if new_email:
                s["email"] = new_email
            s["password"] = new_password
            if new_qualification:
                s["qualification"] = new_qualification
            if new_contact:
                s["contact"] = new_contact

            staff[idx] = s
            data["staff"] = staff
            save_data(data)
            print(f"Staff with id {user_id} updated successfully.\n")
            return
    print(f"No staff found with id {user_id}.\n")

def delete_staff(data):
    print("\n--- Delete Staff ---")
    if not admin_authenticate(data):
        return
    staff = data.get("staff", [])
    if not staff:
        print("No staff records to delete.\n")
        return
    try:
        user_id = int(input("Enter staff id to delete: ").strip())
    except ValueError:
        print("Invalid id (must be a number).")
        return
    for idx, s in enumerate(staff):
        if s["id"] == user_id:
            print("\nFound record:")
            print_staff_record(s)
            confirm = input(f"Are you sure you want to delete staff id {user_id}? (y/N): ").strip().lower()
            if confirm == "y":
                staff.pop(idx)
                data["staff"] = staff
                save_data(data)
                print(f"Staff with id {user_id} deleted successfully.\n")
            else:
                print("Deletion cancelled.\n")
            return
    print(f"No staff found with id {user_id}.\n")

def view_all_staff(data):
    print("\n--- All Staff Records ---")
    staff = data.get("staff", [])
    if not staff:
        print("No staff records.\n")
        return
    for s in staff:
        print_staff_record(s)
    print("")

# ---------------------------
# Main Menu
# ---------------------------

def main_menu():
    data = load_data()
    print("Staff Registration System")
    print("-------------------------")
    while True:
        print("Menu:")
        print("1 - Add information of staff")
        print("2 - Search staff (by id, email, password)")
        print("3 - Update any staff information")
        print("4 - Delete any staff information")
        print("5 - View all staff information")
        print("6 - Exit")
        choice = input("Choose option (1-6): ").strip()

        if choice == "1":
            add_staff(data)
        elif choice == "2":
            search_staff(data)
        elif choice == "3":
            update_staff(data)
        elif choice == "4":
            delete_staff(data)
        elif choice == "5":
            view_all_staff(data)
        elif choice == "6":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number 1-6.\n")

if __name__ == "__main__":
    main_menu()