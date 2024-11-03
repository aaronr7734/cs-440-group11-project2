"""
This file implements the repository pattern for wishlist operations,
handling all database interactions related to user wishlists including
creating new entries and retrieving existing ones.

Classes:
    WishlistRepository: Manages wishlist data persistence and retrieval
"""

import sqlite3
from typing import List
from ..models.wishlist import WishlistEntry


class WishlistRepository:
    def __init__(self, db_connection):
        self.db = db_connection  # Now stores DatabaseConnection instance instead of direct connection

    def get_by_user(self, account_id: int) -> List[WishlistEntry]:
        with self.db.get_users_connection() as conn:  # Use context manager
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Wishlist WHERE account_id = ?", (account_id,))
            return [WishlistEntry.from_db_row(row) for row in cursor.fetchall()]

    def create(self, entry: WishlistEntry) -> bool:
        try:
            with self.db.get_users_connection() as conn:  # Use context manager
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM Wishlist WHERE account_id = ? AND book_id = ?",
                    (entry.account_id, entry.book_id),
                )
                if cursor.fetchone():
                    return False

                cursor.execute(
                    "INSERT INTO Wishlist (account_id, book_id) VALUES (?, ?)",
                    (entry.account_id, entry.book_id),
                )
                return True
        except sqlite3.Error:
            return False
