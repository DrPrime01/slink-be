import secrets
import re


def generate_short_id(chars_length: int):
    """Function to generate short_id of specified length of characters"""
    nbytes = (chars_length * 3) // 4
    return secrets.token_urlsafe(nbytes)[:chars_length]


def is_valid_email(email):
    """Function to validate email with regex"""
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_pattern, email) is not None
