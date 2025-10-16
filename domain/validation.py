
import re


def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(pattern, email) is not None


def validate_contact(contact: str) -> bool:
    # simple numeric phone validation (10 digits)
    return contact.isdigit() and (7 <= len(contact) <= 13)


def validate_nonempty(value: str) -> bool:
    return bool(value and value.strip())


def is_admin(staff_id: int) -> bool:
    return int(staff_id) == 100

