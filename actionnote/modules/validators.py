"""
Validators Module
Small shared input-validation helpers
"""


def is_valid_password(password: str) -> bool:
    """A password must be at least 8 characters and include a letter and a digit"""
    return (
        len(password) >= 8
        and any(c.isalpha() for c in password)
        and any(c.isdigit() for c in password)
    )
