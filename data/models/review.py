"""
Defines the Review data class and provides a method to create a Review instance from a database row.

Classes:
    Review: A data class representing a book review.

Methods:
    Review.from_db_row(row): A static method that creates a Review instance from a database row.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Review:
    review_id: Optional[int]
    account_id: int
    book_id: int
    rating_score: float
    review_title: str
    review_text: str

    @staticmethod
    def from_db_row(row) -> "Review":
        return Review(
            review_id=row[0],
            account_id=row[1],
            book_id=row[2],
            rating_score=float(row[3]),
            review_title=row[4],
            review_text=row[5],
        )
