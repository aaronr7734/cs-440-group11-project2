"""
This module implements core review operations including creation and retrieval
of book reviews. It serves as a service layer between the API endpoints and data
repositories.

Classes:
    ReviewService: Handles book review management operations
"""

from typing import List, Optional
from data.repositories.review_repo import ReviewRepository
from data.repositories.book_repo import BookRepository
from data.models.review import Review


class ReviewService:
    def __init__(
        self, review_repository: ReviewRepository, book_repository: BookRepository
    ):
        self.review_repo = review_repository
        self.book_repo = book_repository

    def get_book_reviews(self, book_id: int) -> List[Review]:
        """Get all reviews for a book"""
        return self.review_repo.get_by_book_id(book_id)

    def get_user_review(self, account_id: int, book_id: int) -> Optional[Review]:
        """Get a specific user's review for a book"""
        return self.review_repo.get_user_review(account_id, book_id)

    def add_review(
        self,
        account_id: int,
        book_id: int,
        rating: float,
        review_title: str,
        review_text: str,
    ) -> bool:
        """Add a new review if one doesn't exist for this user and book"""
        # Validate rating
        try:
            rating_float = float(rating)
            if not (1 <= rating_float <= 5):
                return False
        except ValueError:
            return False

        # Create and save review
        review = Review(
            None, account_id, book_id, rating_float, review_title, review_text
        )
        return self.review_repo.create(review)
