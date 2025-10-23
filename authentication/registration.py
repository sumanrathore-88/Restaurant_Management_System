import os
import json
import getpass
from domain.menu_order import MenuOrder
from domain.validation import validate_email, validate_password, validate_non_empty_string, validate_id
from domain.logs import log_event

# This module is called from main.py

def admin_login_prompt(menu_order):
    print("Admin login required")
    uid = input("Admin ID: ").strip()
    pwd = getpass.getpass("Password: ")
    user = menu_order.authenticate(uid, pwd)
    if user and user.get("role") == "admin":
        print("Admin authenticated.")
        return user
    print("Admin authentication failed.")
    return None

def staff_signup(menu_order):
    # Signup (only admin can create staff)
    admin = admin_login_prompt(menu_order)
    if not admin:
        return
    print("Register new staff")
    sid = input("Staff ID (numeric): ").strip()
    if not sid.isdigit():
        print("Invalid id")
        return
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    pwd = getpass.getpass("Password: ")
    contact = input("Contact: ").strip()
    qualification = input("Qualification: ").strip()
    if not validate_non_empty_string(name) or not validate_email(email) or not validate_password(pwd):
        print("Invalid details.")
        return
    staff_obj = {
        "id": int(sid),
        "name": name,
        "email": email,
        "password": pwd,
        "contact": contact,
        "qualification": qualification
    }
    try:
        menu_order.add_staff(staff_obj, admin_actor=admin)
        print("Staff registered successfully.")
    except Exception as e:
        print("Failed to register staff:", e)

def signin(menu_order):
    print("Sign In")
    uid = input("ID: ").strip()
    pwd = getpass.getpass("Password: ")
    actor = menu_order.authenticate(uid, pwd)
    if not actor:
        print("Invalid credentials.")
        log_event("WARNING", f"Failed login attempt id {uid}")
        return
    print(f"Welcome {actor.get('name')} ({actor.get('role')})")
    log_event("INFO", f"User signed in: {actor.get('name')}", actor=actor.get("name"))
    # after login show menu actions
    while True:
        print("\nActions: 1) View Menu  2) Take Order  3) Book Table  4) Modify Menu (admin only) 5) Logout")
        ch = input("Choice: ").strip()
        if ch == "1":
            menu_order.view_menu()
        elif ch == "2":
            menu_order.view_menu()
            menu_order.take_order(actor)
        elif ch == "3":
            cust = input("Customer name: ").strip()
            contact = input("Contact (optional): ").strip()
            if not cust:
                print("Invalid customer name.")
                continue
            menu_order.book_table(cust, contact)
        elif ch == "4":
            if actor.get("role") == "admin":
                menu_order.admin_modify_menu(actor)
            else:
                print("Only admin can modify menu.")
        elif ch == "5":
            print("Logging out.")
            break
        else:
            print("Invalid choice.")

def main_menu():
    menu_order = MenuOrder()
    while True:
        print("\nCHATORA - Welcome")
        print("1) Sign in")
        print("2) Sign up (admin only - register staff)")
        print("3) Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            signin(menu_order)
        elif choice == "2":
            staff_signup(menu_order)
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")
