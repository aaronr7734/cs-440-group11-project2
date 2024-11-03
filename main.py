from flask import Flask
from app.routes import routes


def create_app():
    """Initialize and configure the Flask application"""
    app = Flask(__name__, static_folder="app/static", template_folder="app/templates")

    # Set secret key for session management
    app.secret_key = "BooksListSecretKey"

    # Register all routes from routes.py
    for route, view_func in routes.items():
        app.add_url_rule(route, view_func=view_func, methods=["GET", "POST"])

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=False)
