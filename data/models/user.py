"""
This file defines the User dataclass which represents a user entity with attributes
such as id, username, email, and hashed_password. It also includes a static method
to create a User instance from a database row.

Classes:
    User: A dataclass representing a user with id, username, email, and hashed_password attributes.

Methods:
    User.from_db_row(row): A static method that creates a User instance from a database row.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    hashed_password: str

    @staticmethod
    def from_db_row(row) -> "User":
        return User(id=row[0], username=row[1], email=row[2], hashed_password=row[3])
