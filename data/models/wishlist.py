"""
This file defines the WishlistEntry data class which represents an entry in a user's wishlist.

Classes:
    WishlistEntry: A data class that holds information about a wishlist entry, including the account ID and book ID.

Methods:
    from_db_row(row): A static method that creates a WishlistEntry instance from a database row.
"""

from dataclasses import dataclass


@dataclass
class WishlistEntry:
    account_id: int
    book_id: int

    @staticmethod
    def from_db_row(row) -> "WishlistEntry":
        return WishlistEntry(account_id=row[0], book_id=row[1])
