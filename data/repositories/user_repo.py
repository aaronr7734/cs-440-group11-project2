"""
This file provides the UserRepository class which manages all database interactions
for User entities, including creating, retrieving, and authenticating user records.
It uses SQLite as the underlying database and provides type-safe operations
through the User model class.

Classes:
    UserRepository: Handles all database operations for User entities

"""

import sqlite3
from typing import Optional
from ..models.user import User


class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection  # Now stores DatabaseConnection instance instead of direct connection

    def get_by_username(self, username: str) -> Optional[User]:
        with self.db.get_users_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE user_name = ?", (username,))
            row = cursor.fetchone()
            return User.from_db_row(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        with self.db.get_users_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
            row = cursor.fetchone()
            return User.from_db_row(row) if row else None

    def create(self, user: User) -> bool:
        try:
            with self.db.get_users_connection() as conn:  # Use context manager
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO User (user_name, email, hashed_password) VALUES (?, ?, ?)",
                    (user.username, user.email, user.hashed_password),
                )
                return True
        except sqlite3.Error:
            return False

    def user_exists(self, username: str, email: str) -> bool:
        with self.db.get_users_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM User WHERE user_name = ? OR email = ?", (username, email)
            )
            return len(cursor.fetchall()) > 0
