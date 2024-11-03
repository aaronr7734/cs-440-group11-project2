"""
This file provides the BookRepository class which manages all database interactions
for Book entities, including creating, retrieving, and querying book records.
It uses SQLite as the underlying database and provides type-safe operations
through the Book model class.

Classes:
    BookRepository: Handles all database operations for Book entities
"""

import sqlite3
from typing import List, Optional
from ..models.book import Book


class BookRepository:
    def __init__(self, db_connection):
        self.db = db_connection  # Now stores DatabaseConnection instance instead of direct connection

    def get_by_id(self, book_id: int) -> Optional[Book]:
        with self.db.get_books_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Book WHERE id = ?", (book_id,))
            row = cursor.fetchone()
            return Book.from_db_row(row) if row else None

    def get_all(self) -> List[Book]:
        with self.db.get_books_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Book")
            return [Book.from_db_row(row) for row in cursor.fetchall()]

    def create(self, book: Book) -> bool:
        try:
            with self.db.get_books_connection() as conn:  # Use context manager
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM Book WHERE title = ? AND author = ?",
                    (book.title, book.author),
                )
                if cursor.fetchone():
                    return False

                cursor.execute(
                    "INSERT INTO Book (title, author, rating_avg) VALUES (?, ?, ?)",
                    (book.title, book.author, book.rating_avg),
                )
                return True
        except sqlite3.Error:
            return False
