from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


def validate_text(text):
    text = text.strip()
    if len(text) > 0:
        return True
    else:
        return False


def validate_name(name):
    if validate_text(name):
        if name.isalpha():
            return True
    return False


def validate_nric(nric):
    if not validate_text(nric):
        return False
    if len(nric) != 9:
        return False
    if not nric[1:8].isdigit():
        return False
    if nric[0] not in ["S", "T", "F", "G"] and nric[-1] not in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "Z", "J"]:
        return False
    return True


def validate_contact_number(c):
    if len(c) != 8 or not c.isdigit():
        return False
    return True


def validate_email(email):
    if validate_text(email):
        if email.count("@") == 1 and email.endswith(".com"):
            return True
    return False


def validate_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def validate_password(password, confirm_password):
    password_hash = generate_password_hash(password)
    return check_password_hash(password_hash, confirm_password)
