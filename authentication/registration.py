
from __future__ import annotations
import os
import json
import getpass
from typing import Optional, Dict, Any, List


try:
    from domain.validation import Validation
except Exception:
    Validation = None  

try:
    from domain.logs import Logger, get_logger  
except Exception:
    Logger = None
    get_logger = None


MenuOrder = None
menu_order_module = None
try:
    from domain.menu_order import MenuOrder
except Exception:
    MenuOrder = None
    try:
        import importlib

        menu_order_module = importlib.import_module("domain.menu_order")
    except Exception:
        menu_order_module = None

TableBooking = None
table_booking_module = None
try:
    from domain.table_booking import TableBooking
except Exception:
    TableBooking = None
    try:
        import importlib

        table_booking_module = importlib.import_module("domain.table_booking")
    except Exception:
        table_booking_module = None

Report = None
report_module = None
try:
    
    from report.report import Report
except Exception:
    Report = None
    try:
        import importlib

        report_module = importlib.import_module("report.report")
    except Exception:
        report_module = None

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # package root (RESTAURANT_MANAGEMENT_SYSTEM/authentication -> ..)
DB_DIR = os.path.join(BASE_DIR, "database")
STAFF_FILE = os.path.join(DB_DIR, "staff.json")

# Hard-coded admin as required
ADMIN = {"id": 100, "name": "suman rathore", "email": "suman@gmail.com", "password": "suman123"}


# -------------------------
# Fallback simple Validation & Logger 
# -------------------------
if Validation is None:
    class Validation:
        """Minimal fallback Validation used only if domain.validation is missing."""
        @staticmethod
        def non_empty(v) -> bool:
            return bool(v and str(v).strip())

        @staticmethod
        def is_valid_id(v) -> bool:
            try:
                return int(v) > 0
            except Exception:
                return False

        @staticmethod
        def is_valid_email(e: str) -> bool:
            try:
                s = str(e).strip()
                return "@" in s and "." in s and len(s) >= 5
            except Exception:
                return False

        @staticmethod
        def is_valid_password(p: str) -> bool:
            try:
                return isinstance(p, str) and len(p.strip()) >= 4
            except Exception:
                return False

        @staticmethod
        def is_valid_contact(c: str) -> bool:
            try:
                s = str(c).strip()
                return s.isdigit() and len(s) == 10
            except Exception:
                return False


if Logger is None:
    
    import datetime

    class Logger:
        def __init__(self):
            os.makedirs(DB_DIR, exist_ok=True)
            self.path = os.path.join(DB_DIR, "logs.txt")

        def _write(self, level: str, msg: str):
            try:
                ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
                line = f"[{ts}] {level}: {msg}\n"
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                
                try:
                    print(f"{level}: {msg}")
                except Exception:
                    pass

        def info(self, msg: str):
            self._write("INFO", msg)

        def warning(self, msg: str):
            self._write("WARNING", msg)

        def error(self, msg: str):
            self._write("ERROR", msg)



try:
    _logger = get_logger() if get_logger else Logger()
except Exception:
    _logger = Logger()


# -------------------------
# Registration class
# -------------------------
class Registration:
    def __init__(self, staff_db_path: str = STAFF_FILE):
        os.makedirs(os.path.dirname(staff_db_path), exist_ok=True)
        self.staff_db_path = staff_db_path
        self.validation = Validation()
        self.logger = _logger
        # ensure staff file exists and is a list
        if not os.path.exists(self.staff_db_path):
            try:
                with open(self.staff_db_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
                self.logger.info(f"Created staff DB at {self.staff_db_path}")
            except Exception as e:
                self.logger.error(f"Failed to create staff DB: {e}")

    
    def _load_staff(self) -> List[Dict[str, Any]]:
        try:
            with open(self.staff_db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            self.logger.warning("staff.json format invalid; resetting to empty list.")
            return []
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            self.logger.error("staff.json malformed; returning empty staff list.")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error loading staff DB: {e}")
            return []

    def _save_staff(self, staff_list: List[Dict[str, Any]]) -> bool:
        try:
            with open(self.staff_db_path, "w", encoding="utf-8") as f:
                json.dump(staff_list, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save staff DB: {e}")
            return False

    def _find_staff_by_id(self, staff_list: List[Dict[str, Any]], staff_id: int) -> Optional[Dict[str, Any]]:
        for s in staff_list:
            try:
                if int(s.get("id")) == int(staff_id):
                    return s
            except Exception:
                continue
        return None

    def _find_staff_by_email(self, staff_list: List[Dict[str, Any]], email: str) -> Optional[Dict[str, Any]]:
        for s in staff_list:
            if str(s.get("email", "")).lower() == str(email).lower():
                return s
        return None

    # ---------- admin authenticate ----------
    def _admin_authenticate(self) -> bool:
        """Simple admin auth using the hard-coded ADMIN credentials."""
        try:
            print("Admin authentication required.")
            aid = input("Admin ID: ").strip()
            aemail = input("Admin Email: ").strip()
            apw = getpass.getpass("Admin Password: ").strip()
            if not (self.validation.is_valid_id(aid) and self.validation.is_valid_email(aemail)):
                print("Invalid admin credential format.")
                self.logger.warning("Admin provided invalid credential format.")
                return False
            if int(aid) == ADMIN["id"] and aemail.lower() == ADMIN["email"].lower() and apw == ADMIN["password"]:
                self.logger.info("Admin authenticated successfully.")
                return True
            print("Admin authentication failed.")
            self.logger.warning("Admin authentication failed.")
            return False
        except Exception as e:
            self.logger.error(f"Exception during admin authentication: {e}")
            return False

    # ---------- staff management (admin-only) ----------
    def add_staff(self):
        if not self._admin_authenticate():
            return
        try:
            staff_list = self._load_staff()
            raw_id = input("Enter Staff ID: ").strip()
            if not self.validation.is_valid_id(raw_id):
                print("Invalid ID.")
                return
            staff_id = int(raw_id)
            if self._find_staff_by_id(staff_list, staff_id):
                print("Staff with this ID already exists.")
                return
            name = input("Name: ").strip()
            if not self.validation.non_empty(name):
                print("Name cannot be empty.")
                return
            email = input("Email: ").strip()
            if not self.validation.is_valid_email(email):
                print("Invalid email.")
                return
            if self._find_staff_by_email(staff_list, email):
                print("Email already in use.")
                return
            password = getpass.getpass("Password: ").strip()
            if not self.validation.is_valid_password(password):
                print("Password does not meet requirements.")
                return
            contact = input("Contact number (10 digits): ").strip()
            if not self.validation.is_valid_contact(contact):
                print("Invalid contact number.")
                return
            qualification = input("Qualification: ").strip()
            if not self.validation.non_empty(qualification):
                print("Qualification cannot be empty.")
                return
            new = {
                "id": staff_id,
                "name": name,
                "email": email,
                "password": password,
                "contact": contact,
                "qualification": qualification,
            }
            staff_list.append(new)
            if self._save_staff(staff_list):
                print("Staff added successfully.")
                self.logger.info(f"Admin added staff {staff_id} - {name}")
            else:
                print("Failed to add staff (save error).")
        except Exception as e:
            print("Error while adding staff.")
            self.logger.error(f"add_staff exception: {e}")

    def update_staff(self):
        if not self._admin_authenticate():
            return
        try:
            staff_list = self._load_staff()
            raw_id = input("Enter Staff ID to update: ").strip()
            if not self.validation.is_valid_id(raw_id):
                print("Invalid ID.")
                return
            staff = self._find_staff_by_id(staff_list, int(raw_id))
            if not staff:
                print("Staff not found.")
                return
            print(f"Updating staff {staff.get('id')} - {staff.get('name')}")
            name = input(f"Name [{staff.get('name')}]: ").strip() or staff.get('name')
            email = input(f"Email [{staff.get('email')}]: ").strip() or staff.get('email')
            if not self.validation.is_valid_email(email):
                print("Invalid email.")
                return
            contact = input(f"Contact [{staff.get('contact')}]: ").strip() or staff.get('contact')
            if not self.validation.is_valid_contact(contact):
                print("Invalid contact.")
                return
            qualification = input(f"Qualification [{staff.get('qualification')}]: ").strip() or staff.get('qualification')
            change_pw = input("Change password? (y/N): ").strip().lower()
            if change_pw == "y":
                pw = getpass.getpass("New password: ").strip()
                if not self.validation.is_valid_password(pw):
                    print("Invalid password.")
                    return
                staff["password"] = pw
            staff["name"] = name
            staff["email"] = email
            staff["contact"] = contact
            staff["qualification"] = qualification
            if self._save_staff(staff_list):
                print("Staff updated.")
                self.logger.info(f"Admin updated staff {staff.get('id')}")
            else:
                print("Failed to save staff updates.")
        except Exception as e:
            print("Error while updating staff.")
            self.logger.error(f"update_staff exception: {e}")

    def delete_staff(self):
        if not self._admin_authenticate():
            return
        try:
            staff_list = self._load_staff()
            raw_id = input("Enter Staff ID to delete: ").strip()
            if not self.validation.is_valid_id(raw_id):
                print("Invalid ID.")
                return
            s = self._find_staff_by_id(staff_list, int(raw_id))
            if not s:
                print("Staff not found.")
                return
            confirm = input(f"Confirm delete {s.get('id')} - {s.get('name')}? (y/N): ").strip().lower()
            if confirm != "y":
                print("Deletion cancelled.")
                return
            staff_list = [x for x in staff_list if int(x.get("id")) != int(raw_id)]
            if self._save_staff(staff_list):
                print("Staff deleted.")
                self.logger.info(f"Admin deleted staff {raw_id}")
            else:
                print("Failed to delete staff.")
        except Exception as e:
            print("Error while deleting staff.")
            self.logger.error(f"delete_staff exception: {e}")

    def list_staff(self):
        try:
            staff_list = self._load_staff()
            if not staff_list:
                print("No staff records.")
                return
            print("\n--- Staff List ---")
            for s in staff_list:
                print(f"ID:{s.get('id')} | Name:{s.get('name')} | Email:{s.get('email')} | Contact:{s.get('contact')} | Qualification:{s.get('qualification')}")
            print("------------------\n")
        except Exception as e:
            print("Error listing staff.")
            self.logger.error(f"list_staff exception: {e}")

    # ---------- signin / signup flows ----------
    def signup_flow(self):
        """Admin-only management menu"""
        if not self._admin_authenticate():
            return
        while True:
            print("\nAdmin - Staff Management")
            print("1. Add Staff")
            print("2. Update Staff")
            print("3. Delete Staff")
            print("4. List Staff")
            print("5. Back")
            ch = input("Choose: ").strip()
            if ch == "1":
                self.add_staff()
            elif ch == "2":
                self.update_staff()
            elif ch == "3":
                self.delete_staff()
            elif ch == "4":
                self.list_staff()
            elif ch == "5":
                break
            else:
                print("Invalid choice.")

    def signin_flow(self):
        try:
            print("\nSign In")
            identifier = input("Enter Staff ID or Email: ").strip()
            password = getpass.getpass("Password: ").strip()
            # admin check
            if (identifier.isdigit() and int(identifier) == ADMIN["id"]) or (identifier.lower() == ADMIN["email"].lower()):
                if password == ADMIN["password"]:
                    print(f"Welcome Admin {ADMIN['name']}!")
                    self.logger.info("Admin signed in.")
                    self._admin_post_login()
                    return
                else:
                    print("Invalid admin password.")
                    return
            # staff sign-in
            staff_list = self._load_staff()
            staff_member = None
            if identifier.isdigit():
                staff_member = self._find_staff_by_id(staff_list, int(identifier))
            else:
                staff_member = self._find_staff_by_email(staff_list, identifier)
            if not staff_member:
                print("Staff account not found.")
                self.logger.warning("Signin failed - staff not found.")
                return
            if staff_member.get("password") != password:
                print("Incorrect password.")
                self.logger.warning(f"Signin failed for staff {staff_member.get('id')}: incorrect password.")
                return
            print(f"Welcome {staff_member.get('name')}!")
            self.logger.info(f"Staff signed in: {staff_member.get('id')}")
            self._staff_post_login(staff_member)
        except Exception as e:
            print("An error occurred during sign in.")
            self.logger.error(f"signin_flow exception: {e}")

    # ---------- post-login menus ----------
    def _admin_post_login(self):
        while True:
            print("\nAdmin Menu")
            print("1. Staff Management")
            print("2. Open Reports")
            print("3. Table Booking Module")
            print("4. Menu/Order Module")
            print("5. Sign out")
            ch = input("Choose: ").strip()
            if ch == "1":
                self.signup_flow()
            elif ch == "2":
                self._call_report()
            elif ch == "3":
                self._call_table_booking()
            elif ch == "4":
                self._call_menu_order()
            elif ch == "5":
                print("Signing out.")
                break
            else:
                print("Invalid choice.")

    def _staff_post_login(self, staff_member: Dict[str, Any]):
        while True:
            print("\nStaff Menu")
            print("1. Menu/Order Module")
            print("2. Table Booking Module")
            print("3. Generate/View Report (limited)")
            print("4. Sign out")
            ch = input("Choose: ").strip()
            if ch == "1":
                self._call_menu_order()
            elif ch == "2":
                self._call_table_booking()
            elif ch == "3":
                self._call_report(limited=True)
            elif ch == "4":
                print("Signing out.")
                break
            else:
                print("Invalid choice.")

    # ---------- module ----------
    def _call_menu_order(self):
        try:
            # Preferred: MenuOrder class
            if MenuOrder is not None:
                try:
                    mo = MenuOrder()
                    if hasattr(mo, "main"):
                        mo.main()
                        return
                    if hasattr(mo, "take_order"):
                        mo.take_order()
                        return
                except Exception as e:
                    self.logger.error(f"MenuOrder class exists but failed: {e}")
            #  module object
            if menu_order_module is not None:
                try:
                    if hasattr(menu_order_module, "MenuOrder"):
                        mo = menu_order_module.MenuOrder()
                        if hasattr(mo, "main"):
                            mo.main()
                            return
                    if hasattr(menu_order_module, "main"):
                        menu_order_module.main()
                        return
                    if hasattr(menu_order_module, "take_order"):
                        menu_order_module.take_order()
                        return
                except Exception as e:
                    self.logger.error(f"menu_order module invocation failed: {e}")
            print("Menu/Order module not available.")
            self.logger.warning("Attempted to call menu_order but module not found or no entrypoint.")
        except Exception as e:
            print("Error running Menu/Order module.")
            self.logger.error(f"_call_menu_order exception: {e}")

    def _call_table_booking(self):
        try:
            if TableBooking is not None:
                try:
                    tb = TableBooking()
                    if hasattr(tb, "main"):
                        tb.main()
                        return
                except Exception as e:
                    self.logger.error(f"TableBooking class exists but failed: {e}")
            if table_booking_module is not None:
                try:
                    if hasattr(table_booking_module, "TableBooking"):
                        tb = table_booking_module.TableBooking()
                        if hasattr(tb, "main"):
                            tb.main()
                            return
                    if hasattr(table_booking_module, "main"):
                        table_booking_module.main()
                        return
                except Exception as e:
                    self.logger.error(f"table_booking module invocation failed: {e}")
            print("Table Booking module not available.")
            self.logger.warning("Attempted to call table_booking but module not found or no entrypoint.")
        except Exception as e:
            print("Error running Table Booking module.")
            self.logger.error(f"_call_table_booking exception: {e}")

    def _call_report(self, limited: bool = False):
        try:
            # preferred: Report class
            if Report is not None:
                try:
                    rp = Report()
                    if hasattr(rp, "main"):
                        # If limited view is requested, pass a flag if supported
                        if limited and hasattr(rp, "main"):
                            
                            rp.main()
                        else:
                            rp.main()
                        return
                except Exception as e:
                    self.logger.error(f"Report class exists but failed: {e}")
            if report_module is not None:
                try:
                    if hasattr(report_module, "Report"):
                        rp = report_module.Report()
                        if hasattr(rp, "main"):
                            rp.main()
                            return
                    if hasattr(report_module, "main"):
                        report_module.main()
                        return
                except Exception as e:
                    self.logger.error(f"report module invocation failed: {e}")
            print("Report module not available.")
            self.logger.warning("Attempted to call report but module not found or no entrypoint.")
        except Exception as e:
            print("Error running Report module.")
            self.logger.error(f"_call_report exception: {e}")

    # ---------- main interactive entry ----------
    def main_menu(self):
        try:
            while True:
                print("\nCHATORA_RESTAURANT - REGISTRATION")
                print("1. Signup (Admin - manage staff)")
                print("2. Signin (Staff/Admin)")
                print("3. Exit")
                ch = input("Choose an option: ").strip()
                if ch == "1":
                    self.signup_flow()
                elif ch == "2":
                    self.signin_flow()
                elif ch == "3":
                    print("Exiting registration module.")
                    break
                else:
                    print("Invalid option. Please choose 1, 2 or 3.")
        except Exception as e:
            print("Fatal error in registration main menu.")
            self.logger.error(f"main_menu exception: {e}")


# Top-level run() function used by main.py
def run():
    reg = Registration()
    reg.main_menu()


# Allow running directly
if __name__ == "__main__":
    run()
