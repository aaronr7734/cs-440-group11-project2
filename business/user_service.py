"""
This module implements core user operations including account creation,
credential verification, and password encryption. It serves as a service
layer between the API endpoints and data repositories.

Classes:
    UserService: Handles user authentication and account management operations

Note:
    All passwords are encrypted using SHA-256 before storage
"""

import hashlib
from typing import Optional, Tuple
from data.repositories.user_repo import UserRepository
from data.models.user import User


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def _encrypt_password(self, password: str) -> str:
        """Encrypt password using SHA-256"""
        message = hashlib.sha256()
        message.update(password.encode())
        return message.hexdigest()

    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user if username and email don't exist"""
        if self.user_repo.user_exists(username, email):
            return False

        hashed_password = self._encrypt_password(password)
        new_user = User(None, username, email, hashed_password)
        return self.user_repo.create(new_user)

    def verify_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Verify user credentials and return user if valid"""
        hashed_password = self._encrypt_password(password)

        # Try username first
        user = self.user_repo.get_by_username(username_or_email)
        if not user:
            # Try email if username not found
            user = self.user_repo.get_by_email(username_or_email)

        if user and user.hashed_password == hashed_password:
            return user
        return None
