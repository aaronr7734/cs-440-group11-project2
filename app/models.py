import sqlite3
import os
from typing import List, Optional, Dict
import hashlib


class DatabaseManager:
    """
    A class to manage database operations for books and users.

    This class handles all database interactions including initialization,
    book management (CRUD operations), and user account management.

    Attributes:
        books_db (str): Path to the books database file
        users_db (str): Path to the users database file
    """

    def __init__(self):
        """
        Initialize DatabaseManager with paths to books and users databases.
        Creates necessary directories and database files if they don't exist.
        """
        self.books_db = "app/static/database/books.db"
        self.users_db = "app/static/database/accounts.db"
        self._init_databases()

    def _init_databases(self) -> None:
        """
        Initialize both books and users databases.
        Creates the database files and required tables if they don't exist.
        """
        self._init_books_db()
        self._init_users_db()

    def _init_books_db(self) -> None:
        """
        Initialize the books database with required schema.
        Creates a books table with columns for id, title, author, description, isbn, and genre.
        """
        os.makedirs(os.path.dirname(self.books_db), exist_ok=True)
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    description TEXT,
                    isbn TEXT UNIQUE,
                    genre TEXT
                )
            """)
            conn.commit()

    def _init_users_db(self) -> None:
        """
        Initialize the users database with required schema.
        Creates a users table with columns for id, username, password, and email.
        """
        os.makedirs(os.path.dirname(self.users_db), exist_ok=True)
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            """)
            conn.commit()

    # Book-related methods
    def add_book(self, title: str, author: str, description: str = None,
                 isbn: str = None, genre: str = None) -> bool:
        """
        Add a new book to the database.

        Args:
            title (str): The title of the book
            author (str): The author of the book
            description (str, optional): A description of the book
            isbn (str, optional): The ISBN of the book
            genre (str, optional): The genre of the book

        Returns:
            bool: True if book was added successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.books_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO books (title, author, description, isbn, genre)
                    VALUES (?, ?, ?, ?, ?)
                """, (title, author, description, isbn, genre))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def get_book(self, book_id: int) -> Optional[Dict]:
        """
        Retrieve a book by its ID.

        Args:
            book_id (int): The ID of the book to retrieve

        Returns:
            Optional[Dict]: A dictionary containing the book's information,
                          or None if the book was not found
        """
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "title": result[1],
                    "author": result[2],
                    "description": result[3],
                    "isbn": result[4],
                    "genre": result[5]
                }
        return None

    def get_all_books(self) -> List[Dict]:
        """
        Retrieve all books from the database.

        Returns:
            List[Dict]: A list of dictionaries, each containing a book's information
        """
        with sqlite3.connect(self.books_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
            return [{
                "id": book[0],
                "title": book[1],
                "author": book[2],
                "description": book[3],
                "isbn": book[4],
                "genre": book[5]
            } for book in books]

    # User-related methods
    def create_user(self, username: str, password: str, email: str) -> bool:
        """
        Create a new user account.

        Args:
            username (str): The desired username
            password (str): The user's password (will be hashed)
            email (str): The user's email address

        Returns:
            bool: True if user was created successfully, False otherwise
        """
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            with sqlite3.connect(self.users_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password, email)
                    VALUES (?, ?, ?)
                """, (username, hashed_password, email))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def verify_user(self, username: str, password: str) -> bool:
        """
        Verify user credentials.

        Args:
            username (str): The username to verify
            password (str): The password to verify (will be hashed and compared)

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users 
                WHERE username = ? AND password = ?
            """, (username, hashed_password))
            return cursor.fetchone() is not None

    def get_user(self, username: str) -> Optional[Dict]:
        """
        Retrieve user information by username.

        Args:
            username (str): The username of the user to retrieve

        Returns:
            Optional[Dict]: A dictionary containing the user's information (excluding password),
                          or None if the user was not found
        """
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "username": result[1],
                    "email": result[3]
                }
        return None