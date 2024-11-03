"""
BooksList Application - Layered Architecture Implementation

This application allows users to create wishlists of books, add books to be wishlisted,
and rate/review books. This version implements a layered architecture pattern with clear
separation of concerns between layers.

Layer Structure:
---------------
Presentation Layer (presentation/):
   Handles direct user interaction including input validation, form processing,
   and view rendering. Templates and static files are part of this layer.

Application Layer (application/):
   Coordinates activities between the presentation and business layers.
   Manages routing, session handling, and response formatting.

Business Layer (business/):
   Contains core business logic and rules. Handles operations like user
   authentication, book management, and wishlist/review processing.

Data Layer (data/):
   Manages data persistence and retrieval. Implements the repository pattern
   for database operations and defines data models.

Layer Dependencies:
-----------------
Presentation → Application → Business → Data

Key Components:
-------------
- DatabaseConnection: Manages SQLite connections for books and users
- Repositories: Handle CRUD operations for each domain object
- Services: Implement business rules and coordinate operations
- RouteHandler: Manages HTTP routes and coordinates between layers
- Validators/Forms: Handle input validation and form processing

File Organization:
----------------
main.py              - Application entry point and dependency injection
presentation/        - Input validation, forms, and view handling
application/        - Route handling, session management, response formatting
business/           - Core business logic and rules
data/               - Data models and database operations
templates/          - HTML templates
static/             - CSS, JavaScript, and other static files
"""

from flask import Flask
from data.database import DatabaseConnection
from data.repositories.book_repo import BookRepository
from data.repositories.user_repo import UserRepository
from data.repositories.review_repo import ReviewRepository
from data.repositories.wishlist_repo import WishlistRepository
from business.book_service import BookService
from business.user_service import UserService
from business.review_service import ReviewService
from business.wishlist_service import WishlistService
from application.routes import RouteHandler


def create_app() -> Flask:
    """Initialize and configure the Flask application"""
    # Create Flask app
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Set secret key for session management
    app.secret_key = "BooksListSecretKey"

    # Initialize database manager
    database = DatabaseConnection()

    # Initialize repositories with database manager
    book_repo = BookRepository(database)
    user_repo = UserRepository(database)
    review_repo = ReviewRepository(database)
    wishlist_repo = WishlistRepository(database)

    # Initialize services
    book_service = BookService(book_repo)
    user_service = UserService(user_repo)
    review_service = ReviewService(review_repo, book_repo)
    wishlist_service = WishlistService(wishlist_repo, book_repo)

    # Initialize route handler and register routes
    route_handler = RouteHandler(
        user_service=user_service,
        book_service=book_service,
        review_service=review_service,
        wishlist_service=wishlist_service,
    )
    route_handler.register_routes(app)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=False)
