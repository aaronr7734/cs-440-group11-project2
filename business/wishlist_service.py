"""
This module implements core wishlist operations including creation and retrieval
of wishlist entries. It serves as a service layer between the API endpoints and data
repositories.

Classes:
    WishlistService: Handles wishlist management operations
"""

from typing import List
from data.repositories.wishlist_repo import WishlistRepository
from data.repositories.book_repo import BookRepository
from data.models.wishlist import WishlistEntry
from data.models.book import Book


class WishlistService:
    def __init__(
        self, wishlist_repository: WishlistRepository, book_repository: BookRepository
    ):
        self.wishlist_repo = wishlist_repository
        self.book_repo = book_repository

    def get_user_wishlist(self, account_id: int) -> List[Book]:
        """Get all books in user's wishlist"""
        wishlist_entries = self.wishlist_repo.get_by_user(account_id)
        books = []
        for entry in wishlist_entries:
            book = self.book_repo.get_by_id(entry.book_id)
            if book:
                books.append(book)
        return books

    def add_to_wishlist(self, account_id: int, book_id: int) -> bool:
        """Add a book to user's wishlist if it exists and isn't already there"""
        # Verify book exists
        book = self.book_repo.get_by_id(book_id)
        if not book:
            return False

        entry = WishlistEntry(account_id, book_id)
        return self.wishlist_repo.create(entry)
