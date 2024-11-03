"""
This module implements route handling and endpoint registration for the web
application. It serves as the main routing layer, coordinating between HTTP
requests, service layer operations, and response formatting.

Classes:
    RouteHandler: Manages route registration and request handling operations

Dependencies:
    - UserService: User authentication and management
    - BookService: Book data operations
    - ReviewService: Book review operations
    - WishlistService: User wishlist management
    - SessionManager: User session handling
    - ResponseFormatter: HTTP response standardization
"""

import json
from flask import request, render_template
from typing import Dict, Any

from business.user_service import UserService
from business.book_service import BookService
from business.review_service import ReviewService
from business.wishlist_service import WishlistService
from .session import SessionManager
from .responses import ResponseFormatter


class RouteHandler:
    def __init__(
        self,
        user_service: UserService,
        book_service: BookService,
        review_service: ReviewService,
        wishlist_service: WishlistService,
    ):
        self.user_service = user_service
        self.book_service = book_service
        self.review_service = review_service
        self.wishlist_service = wishlist_service
        self.session = SessionManager()
        self.response = ResponseFormatter()

    def register_routes(self, app) -> None:
        """Register all routes with the Flask app"""
        routes = {
            "/": self.index_page,
            "/index": self.index_page,
            "/registration": self.registration_page,
            "/signin": self.signin_page,
            "/dashboard": self.dashboard_page,
            "/books": self.books_page,
            "/description": self.description_page,
            "/logoff": self.logoff_page,
            "/wishlist": self.read_wishlist,
            "/book": self.get_books,
            "/add": self.add_page,
            "/get": self.get_page,
        }

        for route, handler in routes.items():
            app.add_url_rule(route, view_func=handler, methods=["GET", "POST"])

    def index_page(self):
        """The index page"""
        if self.session.is_authenticated():
            return self.response.redirect_with_message("/dashboard")
        return self.response.redirect_with_message("/signin")

    def registration_page(self):
        """The registration page"""
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            if self.user_service.create_user(username, email, password):
                return self.response.redirect_with_message("/dashboard")
            return (
                render_template("registration.html")
                + '<script>alert("Could not create account, possibly exists already")</script>'
            )

        return render_template("registration.html")

    def signin_page(self):
        """The signin page"""
        if request.method == "POST":
            username_email = request.form["name_email"]
            password = request.form["password"]

            user = self.user_service.verify_user(username_email, password)
            if user:
                self.session.create_session(user.id, user.username, user.email)
                return self.response.redirect_with_message(
                    "/dashboard", "Signed in successfully!"
                )
            return (
                render_template("signin.html")
                + '<script>alert("Could not sign in, either email/username or password are incorrect");</script>'
            )

        return render_template("signin.html")

    def dashboard_page(self):
        """The dashboard page"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/index")
        return render_template("dashboard.html")

    def books_page(self):
        """The books page"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/")
        return render_template("books.html")

    def description_page(self):
        """The book description page"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/")

        description_data = render_template("description.html")
        if request.args.get("book_id"):
            description_data = description_data.replace(
                "BOOKID", request.args["book_id"]
            )
        return description_data

    def logoff_page(self):
        """Log off the user"""
        self.session.clear_session()
        return self.response.redirect_with_message("/signin", "Logged off successfully")

    def read_wishlist(self):
        """Get user's wishlist"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/")

        books = self.wishlist_service.get_user_wishlist(self.session.get_user_id())
        return ", ".join(str(book.id) for book in books)

    def get_books(self):
        """Get book information"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/")

        book_id = request.args.get("id", "")
        if not book_id:
            return "No book found"

        try:
            book_id = int(book_id)
            if book_id >= 1:
                book = self.book_service.get_book(book_id)
                if book:
                    return self.response.success(
                        {
                            "id": book.id,
                            "title": book.title,
                            "author": book.author,
                            "rating": book.rating_avg,
                        }
                    )
            else:
                books = self.book_service.get_all_books()
                # Use ResponseFormatter's success method to match expected format
                return self.response.success(
                    [
                        {
                            "id": book.id,
                            "title": book.title,
                            "author": book.author,
                            "rating": book.rating_avg,
                        }
                        for book in books
                    ]
                )

        except ValueError:
            return "No book found"

        return "No book found"

    def add_page(self):
        """Add books, reviews, or wishlist items"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/")

        add_type = request.args.get("type", "")

        if add_type == "book":
            title = request.form["title"]
            author = request.form["author"]
            if self.book_service.add_book(title, author):
                return self.response.redirect_with_message(
                    "/books", "Added book successfully"
                )
            return self.response.redirect_with_message(
                None, "Failed to add book, already exists"
            )

        elif add_type == "wishlist":
            book_id = int(request.args["book_id"])
            if self.wishlist_service.add_to_wishlist(
                self.session.get_user_id(), book_id
            ):
                return self.response.redirect_with_message(
                    "/books", "Added to wishlist!"
                )
            return self.response.redirect_with_message(
                None, "Failed to add to wishlist"
            )

        elif add_type == "review":
            review_result = self.review_service.add_review(
                self.session.get_user_id(),
                int(request.args["book_id"]),
                float(request.form["rating"]),
                request.form["review_title"],
                request.form["review_text"],
            )
            if review_result:
                return self.response.redirect_with_message(
                    "/books", "Review added successfully."
                )
            return self.response.redirect_with_message(
                None, "Could not add review, possibly already added"
            )

        return self.response.error("Invalid add type")

    def get_page(self):
        """Get reviews"""
        if not self.session.is_authenticated():
            return self.response.redirect_with_message("/")

        type_get = request.args["type"]
        book_id = int(request.args["book_id"])

        if type_get == "user":
            review = self.review_service.get_user_review(
                self.session.get_user_id(), book_id
            )
            if review:
                return self.response.success(
                    {
                        "account_id": review.account_id,
                        "book_id": review.book_id,
                        "rating_score": review.rating_score,
                        "review_title": review.review_title,
                        "review_text": review.review_text,
                    }
                )
        elif type_get == "all":
            reviews = self.review_service.get_book_reviews(book_id)
            return self.response.success(
                [
                    {
                        "account_id": review.account_id,
                        "book_id": review.book_id,
                        "rating_score": review.rating_score,
                        "review_title": review.review_title,
                        "review_text": review.review_text,
                    }
                    for review in reviews
                ]
            )

        return "[]"
