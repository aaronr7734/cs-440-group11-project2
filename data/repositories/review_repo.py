"""
This module provides the ReviewRepository class which manages all database interactions
for Review entities, including creating, retrieving, and querying review records.
It uses SQLite as the underlying database and provides type-safe operations
through the Review model class.

Classes:
    ReviewRepository: Handles all database operations for Review entities
"""

import sqlite3
from typing import List, Optional
from ..models.review import Review


class ReviewRepository:
    def __init__(self, db_connection):
        self.db = db_connection  # Now stores DatabaseConnection instance instead of direct connection

    def get_by_book_id(self, book_id: int) -> List[Review]:
        with self.db.get_books_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Review WHERE book_id = ?", (book_id,))
            return [Review.from_db_row(row) for row in cursor.fetchall()]

    def get_user_review(self, account_id: int, book_id: int) -> Optional[Review]:
        with self.db.get_books_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Review WHERE account_id = ? AND book_id = ?",
                (account_id, book_id),
            )
            row = cursor.fetchone()
            return Review.from_db_row(row) if row else None

    def create(self, review: Review) -> bool:
        try:
            with self.db.get_books_connection() as conn:  # Use context manager
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO Review 
                    (account_id, book_id, rating_score, review_title, review_text)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        review.account_id,
                        review.book_id,
                        review.rating_score,
                        review.review_title,
                        review.review_text,
                    ),
                )
                return True
        except sqlite3.Error:
            return False
