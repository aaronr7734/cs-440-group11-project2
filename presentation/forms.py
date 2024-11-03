"""
This module implements form data structures for handling user input across
the application. It provides standardized data classes for processing and
validating form submissions.

Classes:
    RegistrationForm: User registration data
    SigninForm: User authentication data
    ReviewForm: Book review submission data
    BookForm: Book creation and editing data
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RegistrationForm:
    username: str
    email: str
    password: str


@dataclass
class SigninForm:
    username_email: str
    password: str


@dataclass
class ReviewForm:
    rating: float
    title: str
    text: str
    book_id: int


@dataclass
class BookForm:
    title: str
    author: str

    @classmethod
    def from_request(cls, request_form) -> "BookForm":
        """Create BookForm from request form data"""
        return cls(
            title=request_form.get("title", "").strip(),
            author=request_form.get("author", "").strip(),
        )
