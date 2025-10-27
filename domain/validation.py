

import re
from datetime import datetime
from typing import Any

class Validation:
    
    EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
    CONTACT_RE = re.compile(r"^\+?\d{7,15}$")  

    @staticmethod
    def validate_id(value: Any, *, name: str = "ID"):
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer.")
        if value <= 0:
            raise ValueError(f"{name} must be a positive integer.")

    @staticmethod
    def validate_name(name: Any, *, field: str = "Name"):
        if not isinstance(name, str):
            raise TypeError(f"{field} must be a string.")
        s = name.strip()
        if len(s) < 2:
            raise ValueError(f"{field} must be at least 2 characters long.")

    @classmethod
    def validate_email(cls, email: Any):
        if not isinstance(email, str):
            raise TypeError("Email must be a string.")
        if not cls.EMAIL_RE.match(email.strip()):
            raise ValueError("Invalid email format.")

    @staticmethod
    def validate_password(password: Any, *, min_length: int = 4):
        if not isinstance(password, str):
            raise TypeError("Password must be a string.")
        if len(password) < min_length:
            raise ValueError(f"Password must be at least {min_length} characters long.")

    @classmethod
    def validate_contact(cls, contact: Any):
        if not isinstance(contact, str):
            raise TypeError("Contact must be a string of digits (optionally starting with '+').")
        if not cls.CONTACT_RE.match(contact.strip()):
            raise ValueError("Invalid contact number. Use digits only, optional leading '+', length 7-15.")

    @staticmethod
    def validate_qualification(qualification: Any):
        if not isinstance(qualification, str):
            raise TypeError("Qualification must be a string.")
        if not qualification.strip():
            raise ValueError("Qualification cannot be empty.")

    # ----- Menu-specific validators -----
    @staticmethod
    def validate_item_name(name: Any):
        if not isinstance(name, str):
            raise TypeError("Item name must be a string.")
        if len(name.strip()) < 2:
            raise ValueError("Item name must be at least 2 characters long.")

    @staticmethod
    def validate_type(t: Any):
        if not isinstance(t, str):
            raise TypeError("Type must be a string: 'Veg' or 'Non-Veg'.")
        if t not in ("Veg", "Non-Veg"):
            raise ValueError("Type must be either 'Veg' or 'Non-Veg' (case-sensitive).")

    @staticmethod
    def validate_price(p: Any, *, field: str = "Price"):
        if not isinstance(p, (int, float)):
            raise TypeError(f"{field} must be a number.")
        if p < 0:
            raise ValueError(f"{field} must be non-negative.")

    @staticmethod
    def validate_portion(portion: Any):
        if not isinstance(portion, str):
            raise TypeError("Portion must be a string 'half' or 'full'.")
        if portion not in ("half", "full"):
            raise ValueError("Portion must be 'half' or 'full'.")

    @staticmethod
    def validate_quantity(qty: Any):
        if not isinstance(qty, int):
            raise TypeError("Quantity must be an integer.")
        if qty <= 0:
            raise ValueError("Quantity must be a positive integer.")

    # ----- Table booking validators -----
    @staticmethod
    def validate_table_number(table_no: Any, *, min_table: int = 1, max_table: int = 20):
        if not isinstance(table_no, int):
            raise TypeError("Table number must be an integer.")
        if not (min_table <= table_no <= max_table):
            raise ValueError(f"Table number must be between {min_table} and {max_table}.")

    @staticmethod
    def validate_num_people(n: Any, *, max_people: int = 20):
        if not isinstance(n, int):
            raise TypeError("Number of people must be an integer.")
        if n <= 0 or n > max_people:
            raise ValueError(f"Number of people must be 1..{max_people}.")

    @staticmethod
    def validate_datetime(dt: Any):
        if not isinstance(dt, datetime):
            raise TypeError("Value must be a datetime instance.")

    # ----- Billing / payment validators -----
    @staticmethod
    def validate_payment_method(method: Any):
        if not isinstance(method, str):
            raise TypeError("Payment method must be a string.")
        if method not in ("Cash", "Google Pay", "Netbanking"):
            raise ValueError("Payment method must be one of: 'Cash', 'Google Pay', 'Netbanking'.")

    
    @staticmethod
    def ensure_non_empty_sequence(seq: Any, *, name: str = "Sequence"):
        if not hasattr(seq, "__len__"):
            raise TypeError(f"{name} must be a sequence.")
        if len(seq) == 0:
            raise ValueError(f"{name} must not be empty.")


if __name__ == "__main__":
    
    from datetime import datetime
    try:
        Validation.validate_id(5)
        Validation.validate_name("Suman", field="Admin name")
        Validation.validate_email("suman@gmail.com")
        Validation.validate_password("suman123")
        Validation.validate_contact("+919876543210")
        Validation.validate_qualification("MBA")
        Validation.validate_item_name("Butter Chicken")
        Validation.validate_type("Non-Veg")
        Validation.validate_price(150)
        Validation.validate_portion("full")
        Validation.validate_quantity(2)
        Validation.validate_table_number(10)
        Validation.validate_num_people(4)
        Validation.validate_datetime(datetime.now())
        Validation.validate_payment_method("Cash")
        Validation.ensure_non_empty_sequence([1], name="Order items")
        print("Validation smoke tests passed.")
    except Exception as e:
        print("Validation test failed:", e)
