"""
This module implements core book operations including retrieval and creation
of books. It serves as a service layer between the API endpoints and data 
repositories.

Classes:
    BookService: Handles book management operations
"""

from typing import List, Optional
from data.repositories.book_repo import BookRepository
from data.models.book import Book


class BookService:
    def __init__(self, book_repository: BookRepository):
        self.book_repo = book_repository

    def get_book(self, book_id: int) -> Optional[Book]:
        """Get a single book by ID"""
        return self.book_repo.get_by_id(book_id)

    def get_all_books(self) -> List[Book]:
        """Get all books"""
        return self.book_repo.get_all()

    def add_book(self, title: str, author: str) -> bool:
        """Add a new book if it doesn't exist"""
        if not title.strip() or not author.strip():
            return False

        new_book = Book(None, title.strip(), author.strip(), 0.0)
        return self.book_repo.create(new_book)
