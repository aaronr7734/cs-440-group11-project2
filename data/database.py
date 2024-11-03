"""
    This file provides the DatabaseConnection class which handles the initialization
    and connection management for two SQLite databases:
    - books.db: Stores book information and reviews
    - accounts.db: Stores user accounts and wishlists

    The databases are structured as follows:

    books.db Tables:
        - Book: Stores book information (id, title, author, average rating)
        - Review: Stores book reviews (review_id, account_id, book_id, rating_score, 
          review_title, review_text)

    accounts.db Tables:
        - User: Stores user account information (id, username, email, hashed password)
        - Wishlist: Stores user wishlists (account_id, book_id)

    The module ensures the database files and tables exist, creating them if necessary.
"""

# data/database.py
import sqlite3
import os
from contextlib import contextmanager


class DatabaseConnection:
    def __init__(self):
        self.books_db = "static/database/books.db"
        self.users_db = "static/database/accounts.db"
        self._init_databases()

    def _init_databases(self) -> None:
        os.makedirs(os.path.dirname(self.books_db), exist_ok=True)
        os.makedirs(os.path.dirname(self.users_db), exist_ok=True)

        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Book (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    rating_avg REAL DEFAULT 0
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Review (
                    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    book_id INTEGER,
                    rating_score REAL,
                    review_title TEXT,
                    review_text TEXT
                )
            """
            )

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS User (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Wishlist (
                    account_id INTEGER REFERENCES User(id),
                    book_id INTEGER
                )
            """
            )

    @contextmanager
    def get_books_connection(self):
        """Context manager for books database connection"""
        conn = sqlite3.connect(self.books_db)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def get_users_connection(self):
        """Context manager for users database connection"""
        conn = sqlite3.connect(self.users_db)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
