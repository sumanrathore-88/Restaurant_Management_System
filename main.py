# main.py
from domain import menu_order, table_booking, validation, logs
from authentication import registration
import json
import os
from getpass import getpass

ADMIN_ID = "100"  # fixed admin id per your spec

def ensure_system():
    menu_order.create_menu_if_missing()
    validation.load_tables()  # ensure tables exist
    validation.load_users()   # ensure admin exists

def admin_menu():
    print("\n--- ADMIN MENU ---")
    print("1. View Menu")
    print("2. Add Menu Item")
    print("3. View Recent Logs")
    print("4. Cancel Booking")
    print("5. Exit Admin Menu")
    choice = input("Choose: ").strip()
    if choice == "1":
        menu_order.display_menu()
    elif choice == "2":
        menu_order.add_menu_item(ADMIN_ID)
    elif choice == "3":
        recent = logs.get_recent_logs(20)
        for r in recent:
            print(r)
    elif choice == "4":
        table_booking.cancel_booking(ADMIN_ID)
    elif choice == "5":
        return
    else:
        print("Invalid choice.")

def staff_menu():
    print("\n--- STAFF MENU ---")
    print("1. View Menu")
    print("2. Place Order")
    print("3. Take Order for a Table")
    print("4. Book a Table for Customer")
    print("5. Exit Staff Menu")
    choice = input("Choose: ").strip()
    if choice == "1":
        menu_order.display_menu()
    elif choice == "2":
        staff_name = input("Enter your staff name: ").strip()
        menu_order.place_order(staff_name)
    elif choice == "3":
        staff_name = input("Enter your staff name: ").strip()
        t = input("Table number (or press enter for walk-in): ").strip()
        table_no = int(t) if t else None
        table_booking.take_order_and_pay(staff_name, table_no)
    elif choice == "4":
        table_booking.book_table()
    elif choice == "5":
        return
    else:
        print("Invalid choice.")

def authenticate_admin():
    pwd = getpass("Enter admin password: ")
    if validation.is_admin_credentials_valid(ADMIN_ID, pwd):
        print("Admin authenticated.")
        return True
    else:
        print("Invalid admin credentials.")
        return False

def run():
    ensure_system()
    while True:
        print("\n=== Restaurant Management System ===")
        print("1. Staff")
        print("2. Admin")
        print("3. Registration / Staff Management")
        print("4. Exit")
        ch = input("Choose: ").strip()
        if ch == "1":
            staff_menu()
        elif ch == "2":
            if authenticate_admin():
                while True:
                    admin_menu()
                    cont = input("Admin: do you want to continue? (y/n): ").strip().lower()
                    if cont != "y":
                        break
        elif ch == "3":
            # Calls the registration CLI in authentication/registration.py
            registration.registration_cli_menu()
        elif ch == "4":
            print("Exiting. Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    run()
