"""
This file defines the Book dataclass and provides a method to create a Book instance from a database row.

Classes:
    Book: A dataclass representing a book with attributes id, title, author, and rating_avg.

Methods:
    Book.from_db_row(row): A static method that creates a Book instance from a database row.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: Optional[int]
    title: str
    author: str
    rating_avg: float = 0.0

    @staticmethod
    def from_db_row(row) -> "Book":
        return Book(id=row[0], title=row[1], author=row[2], rating_avg=float(row[3]))
