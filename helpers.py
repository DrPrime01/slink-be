import secrets


def generate_short_id(chars_length: int):
    """Function to generate short_id of specified length of characters"""
    nbytes = (chars_length * 3) // 4
    return secrets.token_urlsafe(nbytes)[:chars_length]
