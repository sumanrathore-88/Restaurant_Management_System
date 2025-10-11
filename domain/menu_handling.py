
import json
import os
from getpass import getpass
from typing import List, Dict, Any

# Admin credentials
ADMIN = {
    "name": "suman rathore",
    "id": 100,
    "email": "suman@gmail.com",
    "password": "suman123",
}

# File paths
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "database"))
MENU_DB = os.path.join(DB_DIR, "menu.json")
os.makedirs(DB_DIR, exist_ok=True)

# ANSI color codes for better visualization
class Col:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDER = "\033[4m"
    END = "\033[0m"

# Predefined 50+ Menu Items
SAMPLE_MENU = [
    {"id": str(i+1), "name": name, "half_plate_rate": half, "full_plate_rate": full}
    for i, (name, half, full) in enumerate([
        ("Butter Chicken", 160, 300), ("Paneer Butter Masala", 130, 250), ("Dal Makhani", 110, 200),
        ("Shahi Paneer", 140, 260), ("Kadai Paneer", 135, 250), ("Chole Bhature", 100, 180),
        ("Rajma Chawal", 90, 170), ("Jeera Rice", 70, 120), ("Veg Biryani", 120, 220), ("Chicken Biryani", 160, 300),
        ("Mutton Biryani", 200, 380), ("Egg Biryani", 110, 200), ("Fish Curry", 180, 340), ("Prawn Curry", 200, 380),
        ("Masala Dosa", 65, 120), ("Plain Dosa", 50, 90), ("Rava Dosa", 70, 130), ("Idli Sambar", 45, 80),
        ("Vada Sambar", 50, 90), ("Pav Bhaji", 85, 150), ("Pani Puri", 60, 100), ("Bhel Puri", 70, 120),
        ("Samosa (2 pcs)", 40, 70), ("Paneer Tikka", 150, 280), ("Chicken Tikka", 170, 320), ("Tandoori Chicken", 200, 380),
        ("Butter Naan", 35, 60), ("Garlic Naan", 40, 70), ("Roti", 10, 20), ("Paratha", 30, 55),
        ("Aloo Gobi", 90, 160), ("Baingan Bharta", 100, 180), ("Palak Paneer", 130, 250), ("Malai Kofta", 140, 260),
        ("Veg Manchurian", 95, 170), ("Hakka Noodles", 85, 150), ("Schezuan Noodles", 100, 180), ("Chicken Noodles", 110, 200),
        ("Veg Fried Rice", 80, 150), ("Egg Fried Rice", 95, 170), ("Chicken Fried Rice", 120, 220), ("Momos Veg", 70, 120),
        ("Momos Chicken", 90, 160), ("Spring Roll", 80, 140), ("Tomato Soup", 60, 110), ("Hot & Sour Soup", 70, 130),
        ("Sweet Corn Soup", 65, 120), ("French Fries", 75, 140), ("Grilled Sandwich", 80, 140), ("Cheese Sandwich", 95, 170),
        ("Paneer Wrap", 100, 180), ("Chicken Wrap", 120, 220), ("Veg Burger", 90, 160), ("Chicken Burger", 120, 220),
        ("Cold Coffee", 60, 110), ("Masala Chai", 25, 40), ("Lassi", 55, 100)
    ])
]

def load_menu() -> List[Dict[str, Any]]:
    if not os.path.exists(MENU_DB):
        save_menu(SAMPLE_MENU)
        return SAMPLE_MENU
    try:
        with open(MENU_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) >= 50:
                return data
            else:
                save_menu(SAMPLE_MENU)
                return SAMPLE_MENU
    except Exception:
        save_menu(SAMPLE_MENU)
        return SAMPLE_MENU

def save_menu(items: List[Dict[str, Any]]) -> None:
    with open(MENU_DB, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)

def authenticate_admin() -> bool:
    print(f"{Col.HEADER}--- Admin Authentication Required (Menu Management) ---{Col.END}")
    email = input("Admin email: ").strip()
    pw = getpass("Admin password: ")
    if email == ADMIN["email"] and pw == ADMIN["password"]:
        print(f"{Col.GREEN}Authentication successful. Welcome, {ADMIN['name']}!{Col.END}")
        return True
    print(f"{Col.RED}Authentication failed. Access denied.{Col.END}")
    return False

def print_menu(items: List[Dict[str, Any]], title: str = "MENU") -> None:
    print()
    print(f"{Col.CYAN}{Col.BOLD}{title.center(80)}{Col.END}")
    print(f"{Col.YELLOW}{'='*80}{Col.END}")
    print(f"{Col.BOLD}{Col.BLUE}{'ID':<5}{'ITEMS':<35}{'HALF RATE (₹)':<20}{'FULL RATE (₹)':<20}{Col.END}")
    print(f"{Col.YELLOW}{'-'*80}{Col.END}")
    for it in items:
        print(f"{Col.GREEN}{it.get('id', ''):<5}{Col.END}"
              f"{Col.CYAN}{it.get('name', ''):<35}{Col.END}"
              f"{Col.YELLOW}{str(it.get('half_plate_rate')):<20}{Col.END}"
              f"{Col.YELLOW}{str(it.get('full_plate_rate')):<20}{Col.END}")
    print(f"{Col.YELLOW}{'='*80}{Col.END}")

def staff_view_menu() -> None:
    items = load_menu()
    print_menu(items, title="CHATORA _RESTAURANT")

def admin_view_menu() -> None:
    items = load_menu()
    print_menu(items, title="CHATORA _RESTAURANT")

def add_item(items: List[Dict[str, Any]]) -> None:
    print(f"{Col.HEADER}--- Add Menu Item ---{Col.END}")
    new_id = input("ID: ").strip()
    if any(str(i.get("id")) == new_id for i in items):
        print(f"{Col.RED}Item with this ID already exists. Aborting.{Col.END}")
        return
    name = input("Item name: ").strip()
    try:
        half = float(input("Half plate rate: ").strip())
        full = float(input("Full plate rate: ").strip())
    except ValueError:
        print(f"{Col.RED}Invalid rate entered. Aborting.{Col.END}")
        return
    items.append({"id": new_id, "name": name, "half_plate_rate": half, "full_plate_rate": full})
    save_menu(items)
    print(f"{Col.GREEN}Item added successfully.{Col.END}")

def update_item(items: List[Dict[str, Any]]) -> None:
    print(f"{Col.HEADER}--- Update Menu Item ---{Col.END}")
    item_id = input("Enter ID to update: ").strip()
    idx = next((i for i, it in enumerate(items) if str(it.get('id')) == item_id), -1)
    if idx == -1:
        print(f"{Col.RED}Item not found.{Col.END}")
        return
    it = items[idx]
    print(f"Leave blank to keep current value. Current name: {it.get('name')}")
    name = input("New name: ").strip()
    if name:
        it['name'] = name
    try:
        half = input("New half plate rate: ").strip()
        if half:
            it['half_plate_rate'] = float(half)
        full = input("New full plate rate: ").strip()
        if full:
            it['full_plate_rate'] = float(full)
    except ValueError:
        print(f"{Col.RED}Invalid rate input. Aborting update.{Col.END}")
        return
    items[idx] = it
    save_menu(items)
    print(f"{Col.GREEN}Item updated successfully.{Col.END}")

def delete_item(items: List[Dict[str, Any]]) -> None:
    print(f"{Col.HEADER}--- Delete Menu Item ---{Col.END}")
    item_id = input("Enter ID to delete: ").strip()
    idx = next((i for i, it in enumerate(items) if str(it.get('id')) == item_id), -1)
    if idx == -1:
        print(f"{Col.RED}Item not found.{Col.END}")
        return
    it = items[idx]
    confirm = input(f"Type DELETE to remove {it.get('name')}: ")
    if confirm == "DELETE":
        items.pop(idx)
        save_menu(items)
        print(f"{Col.GREEN}Item deleted.{Col.END}")
    else:
        print("Delete aborted.")

def admin_menu_loop() -> None:
    if not authenticate_admin():
        return
    items = load_menu()
    while True:
        print()
        print(f"{Col.BOLD}Admin Menu:{Col.END}")
        print("1. View menu")
        print("2. Add item")
        print("3. Update item")
        print("4. Delete item")
        print("5. Exit to main application")
        choice = input("Choose (1-5): ").strip()
        if choice == '1':
            admin_view_menu()
        elif choice == '2':
            add_item(items)
            items = load_menu()
        elif choice == '3':
            update_item(items)
            items = load_menu()
        elif choice == '4':
            delete_item(items)
            items = load_menu()
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

def show_menu() -> None:
    while True:
        print()
        print(f"{Col.CYAN}{Col.BOLD}--- MENU HANDLING ---{Col.END}")
        print("1. Staff - View Menu")
        print("2. Admin - Manage Menu")
        print("3. Exit to main application")
        ch = input("Choose (1-3): ").strip()
        if ch == '1':
            staff_view_menu()
        elif ch == '2':
            admin_menu_loop()
        elif ch == '3':
            break
        else:
            print("Invalid choice. Try again.")