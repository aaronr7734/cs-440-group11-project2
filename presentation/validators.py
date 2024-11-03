"""
This module implements input validation for user actions including registration,
authentication, and content creation. It provides standardized validation logic
for form data and API requests.

Classes:
    InputValidator: Handles validation operations for user input
"""

from typing import Tuple, Optional


class InputValidator:
    @staticmethod
    def validate_registration(
        username: str, email: str, password: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate registration input"""
        if not username or len(username.strip()) < 1:
            return False, "Username cannot be empty"

        if not email or "@" not in email:
            return False, "Invalid email format"

        if not password or len(password) < 1:
            return False, "Password cannot be empty"

        return True, None

    @staticmethod
    def validate_signin(
        username_email: str, password: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate signin input"""
        if not username_email or len(username_email.strip()) < 1:
            return False, "Username/Email cannot be empty"

        if not password or len(password) < 1:
            return False, "Password cannot be empty"

        return True, None

    @staticmethod
    def validate_review(
        rating: str, title: str, text: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate review input"""
        try:
            rating_float = float(rating)
            if not (1 <= rating_float <= 5):
                return False, "Rating must be between 1 and 5"
        except ValueError:
            return False, "Invalid rating value"

        if not title or len(title.strip()) < 1:
            return False, "Review title cannot be empty"

        if not text or len(text.strip()) < 1:
            return False, "Review text cannot be empty"

        return True, None
