import sqlite3
import os
from typing import List, Optional, Dict, Union, Tuple
import hashlib
import json


class DatabaseManager:
    """
    A unified database manager for books, users, wishlists and reviews.
    Combines functionality from original User and Book classes.
    """

    def __init__(self):
        """Initialize DatabaseManager with paths to books and users databases."""
        self.books_db = "app/static/database/books.db"
        self.users_db = "app/static/database/accounts.db"
        self._init_databases()

    def _init_databases(self) -> None:
        """Initialize both databases with all required tables."""
        os.makedirs(os.path.dirname(self.books_db), exist_ok=True)
        os.makedirs(os.path.dirname(self.users_db), exist_ok=True)

        # Initialize books database tables
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
            conn.commit()

        # Initialize users database tables
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
            conn.commit()

    def _encrypt(self, text: str) -> str:
        """Encrypt text using SHA-256."""
        message = hashlib.sha256()
        message.update(text.encode())
        return message.hexdigest()

    # User Management Methods
    def create_user(self, username: str, password: str, email: str) -> bool:
        """Create a new user account."""
        if self.account_exists(username, email):
            return False

        try:
            with sqlite3.connect(self.users_db) as conn:
                cursor = conn.cursor()
                hashed_password = self._encrypt(password)
                cursor.execute(
                    "INSERT INTO User (user_name, email, hashed_password) VALUES (?, ?, ?)",
                    (username, email, hashed_password),
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def account_exists(self, username: str, email: str, password: str = None) -> bool:
        """Check if account exists based on username and email."""
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            if password:
                hashed_password = self._encrypt(password)
                cursor.execute(
                    "SELECT * FROM User WHERE (user_name = ? OR email = ?) AND hashed_password = ?",
                    (username, email, hashed_password),
                )
            else:
                cursor.execute(
                    "SELECT * FROM User WHERE user_name = ? OR email = ?",
                    (username, email),
                )
            return len(cursor.fetchall()) > 0

    def verify_user(self, username_or_email: str, password: str) -> bool:
        """Verify user credentials."""
        return self.account_exists(username_or_email, username_or_email, password)

    def get_user(self, username: str) -> Optional[Dict]:
        """Get user information by username."""
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE user_name = ?", (username,))
            result = cursor.fetchone()
            if result:
                return {"id": result[0], "username": result[1], "email": result[2]}
        return None

    # Book Management Methods
    def add_book(self, title: str, author: str, rating: float = 0) -> bool:
        """Add a new book to the database."""
        try:
            with sqlite3.connect(self.books_db) as conn:
                cursor = conn.cursor()
                # Check if book exists
                cursor.execute(
                    "SELECT * FROM Book WHERE title = ? AND author = ?", (title, author)
                )
                if cursor.fetchone():
                    return False

                cursor.execute(
                    "INSERT INTO Book (title, author, rating_avg) VALUES (?, ?, ?)",
                    (title, author, rating),
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def get_book(self, book_id: int) -> Optional[Dict]:
        """Get book information by ID."""
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Book WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "title": result[1],
                    "author": result[2],
                    "rating": float(result[3]),
                }
        return None

    def get_all_books(self) -> List[Dict]:
        """Get all books from the database."""
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Book")
            books = cursor.fetchall()
            return [
                {
                    "id": book[0],
                    "title": book[1],
                    "author": book[2],
                    "rating": float(book[3]),
                }
                for book in books
            ]

    # Wishlist Management Methods
    def add_wishlist(
        self, account_id: Union[str, int], book_id: Union[str, int]
    ) -> bool:
        """Add a book to user's wishlist."""
        try:
            with sqlite3.connect(self.users_db) as conn:
                cursor = conn.cursor()
                # Check if already in wishlist
                cursor.execute(
                    "SELECT * FROM Wishlist WHERE account_id = ? AND book_id = ?",
                    (account_id, book_id),
                )
                if cursor.fetchone():
                    return False

                cursor.execute(
                    "INSERT INTO Wishlist (account_id, book_id) VALUES (?, ?)",
                    (account_id, book_id),
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def get_wishlist(self, account_id: int) -> List[Tuple]:
        """Get user's wishlist."""
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT book_id FROM Wishlist WHERE account_id = ?", (account_id,)
            )
            return cursor.fetchall()

    # Review Management Methods
    def add_review(
        self,
        account_id: int,
        book_id: int,
        rating_score: float,
        review_title: str,
        review_text: str,
    ) -> bool:
        """Add a review for a book."""
        try:
            with sqlite3.connect(self.books_db) as conn:
                cursor = conn.cursor()
                # Check if review exists
                cursor.execute(
                    """SELECT * FROM Review 
                    WHERE account_id = ? AND book_id = ? AND rating_score = ? 
                    AND review_title = ? AND review_text = ?""",
                    (account_id, book_id, rating_score, review_title, review_text),
                )
                if cursor.fetchone():
                    return False

                cursor.execute(
                    """INSERT INTO Review 
                    (account_id, book_id, rating_score, review_title, review_text)
                    VALUES (?, ?, ?, ?, ?)""",
                    (account_id, book_id, rating_score, review_title, review_text),
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def get_review(self, account_id: int, book_id: int) -> Optional[str]:
        """Get a specific user's review for a book."""
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Review WHERE account_id = ? AND book_id = ?",
                (account_id, book_id),
            )
            review = cursor.fetchone()
            if review:
                return json.dumps(
                    {
                        "account_id": review[1],
                        "book_id": review[2],
                        "rating_score": float(review[3]),
                        "review_title": review[4],
                        "review_text": review[5],
                    }
                )
        return None

    def get_reviews(self, book_id: int) -> str:
        """Get all reviews for a book."""
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Review WHERE book_id = ?", (book_id,))
            reviews = cursor.fetchall()
            if reviews:
                return json.dumps(
                    [
                        {
                            "account_id": review[1],
                            "book_id": review[2],
                            "rating_score": float(review[3]),
                            "review_title": review[4],
                            "review_text": review[5],
                        }
                        for review in reviews
                    ]
                )
        return "[]"
