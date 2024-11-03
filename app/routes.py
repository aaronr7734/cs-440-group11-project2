from typing import Optional
import json
from flask import request, redirect, session, render_template
from app.models import DatabaseManager


# Initialize database manager
db_manager = DatabaseManager()


def registration_page():
    """The main registration page"""
    registration_data = render_template("registration.html")

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if db_manager.create_user(username, password, email):
            return redirect("/dashboard")
        else:
            registration_data += '<script>alert("Could not create account, possibly exists already")</script>\n'

    return registration_data


def dashboard_page():
    """The dashboard page (consists of wishlist and list of books)"""
    if not _is_user_signed_in():
        return redirect("/index")
    return render_template("dashboard.html")


def signin_page():
    """The main sign in page"""
    signin_data = render_template("signin.html")

    if request.method == "POST":
        user_name_email = request.form["name_email"]
        password = request.form["password"]

        if db_manager.account_exists(
            user_name_email, user_name_email, password=password
        ):
            # Search for the user id, name, and email using password
            user = db_manager.get_user(user_name_email)
            if user:
                session["user_id"] = user["id"]
                session["user_name"] = user["username"]
                session["user_email"] = user["email"]
                signin_data += '<script>alert("Signed in successfully!");window.location.href="/dashboard";</script>'
        else:
            signin_data += '<script>alert("Could not sign in, either email/username or password are incorrect");</script>'

    return signin_data


def index_page():
    """The index page"""
    if _is_user_signed_in():
        return redirect("/dashboard")
    return redirect("/signin")


def read_wishlist():
    """Non-page, returns string containing user's wishlist"""
    if not _is_user_signed_in():
        return redirect("/")

    wishlist = db_manager.get_wishlist(session["user_id"])
    data = ""
    for wishlist_ids in wishlist:
        index = wishlist.index(wishlist_ids)
        for book_id in wishlist_ids:
            if index < (len(wishlist) - 1):
                data += f"{book_id}, "
            else:
                data += f"{book_id}"
    return data


def get_books():
    """Non-page, gets book data based on id. If id < 0, it returns a list of books."""
    if not _is_user_signed_in():
        return redirect("/")

    response = "No book found"

    if request.method == "GET":
        book_id = request.args.get("id", "")
        if book_id != "":
            book_id = int(book_id)
            if book_id == 0:
                book_id += 1

            if book_id >= 1:
                book = db_manager.get_book(book_id)
                response = (
                    json.dumps(book) if book else "No book found"
                )  # Use json.dumps instead of str()
            else:
                books = db_manager.get_all_books()
                response = json.dumps(books) if books else "[]"
    return response


def books_page():
    """The books page, full of all books"""
    if not _is_user_signed_in():
        return redirect("/")
    return render_template("books.html")


def description_page():
    """The description page, contains reviews, title, and author"""
    if not _is_user_signed_in():
        return redirect("/")

    description_data = render_template("description.html")

    if request.method == "GET":
        book_id = request.args.get("book_id", "")
        if book_id:
            description_data = description_data.replace("BOOKID", book_id)

    return description_data


def logoff_page():
    """Logs the user off"""
    session.clear()
    return "<script>alert('Logged off successfully');window.location.href='/signin';</script>"


def add_page():
    """Adds either a book or a review"""
    if not _is_user_signed_in():
        return redirect("/")

    add_type = request.args.get("type", "")
    results = ""

    if add_type == "book":
        title = request.form["title"]
        author = request.form["author"]

        if db_manager.add_book(title, author, 0):
            results += (
                "<script>alert('Added book successfully');history.go(-1);</script>"
            )
        else:
            results += "<script>alert('Failed to add book, already exists');history.go(-1);</script>"

    elif add_type == "wishlist":
        book_id = request.args["book_id"]
        account_id = session["user_id"]

        if not db_manager.add_wishlist(account_id, book_id):
            results += (
                "<script>alert('Failed to add to wishlist');history.go(-1);</script>"
            )
        else:
            results += "<script>alert('Added to wishlist!');history.go(-1);</script>"

    elif add_type == "review":
        account_id = session["user_id"]
        book_id = request.args["book_id"]
        review_title = request.form["review_title"]
        review_text = request.form["review_text"]
        rating = request.form["rating"]

        if db_manager.add_review(
            account_id, book_id, rating, review_title, review_text
        ):
            results += (
                "<script>alert('Review added successfully.');history.go(-1);</script>"
            )
        else:
            results += "<script>alert('Could not add review, possibly already added');history.go(-1);</script>"

    return results


def get_page():
    """Page for getting review"""
    if not _is_user_signed_in():
        return redirect("/")

    type_get = request.args["type"]
    book_id = request.args["book_id"]

    if type_get == "user":
        return str(db_manager.get_review(session["user_id"], book_id))
    elif type_get == "all":
        return str(db_manager.get_reviews(book_id))

    return "[]"


def _is_user_signed_in() -> bool:
    """Returns if a user is signed in"""
    if session is not None:
        try:
            return session.get("user_email") is not None
        except KeyError:
            pass
    return False


# Map of routes to handler functions
routes = {
    "/": index_page,
    "/index": index_page,
    "/registration": registration_page,
    "/signin": signin_page,
    "/dashboard": dashboard_page,
    "/books": books_page,
    "/description": description_page,
    "/logoff": logoff_page,
    "/wishlist": read_wishlist,
    "/book": get_books,
    "/add": add_page,
    "/get": get_page,
}
