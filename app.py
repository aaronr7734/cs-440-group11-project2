import json
import sqlite3
from typing import Optional, Dict
import os
import hashlib
from flask import Flask, request, redirect, session, render_template

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.secret_key = "BooksListSecretKey"

# Global database paths
BOOKS_DB = "static/database/books.db"
USERS_DB = "static/database/accounts.db"

def init_databases():
    """Initialize all database tables in one place"""
    os.makedirs(os.path.dirname(BOOKS_DB), exist_ok=True)
    os.makedirs(os.path.dirname(USERS_DB), exist_ok=True)

    with sqlite3.connect(BOOKS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Book (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                rating_avg REAL DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Review (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                book_id INTEGER,
                rating_score REAL,
                review_title TEXT,
                review_text TEXT
            )
        """)
        conn.commit()

    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Wishlist (
                account_id INTEGER REFERENCES User(id),
                book_id INTEGER
            )
        """)
        conn.commit()

# Initialize databases on startup
init_databases()

# Utility functions
def encrypt_password(password: str) -> str:
    """Encrypt password using SHA-256"""
    message = hashlib.sha256()
    message.update(password.encode())
    return message.hexdigest()

def check_account_exists(username: str, email: str, password: str = None) -> bool:
    """Check if account exists in database"""
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        if password:
            hashed_password = encrypt_password(password)
            cursor.execute(
                "SELECT * FROM User WHERE (user_name = ? OR email = ?) AND hashed_password = ?",
                (username, email, hashed_password)
            )
        else:
            cursor.execute(
                "SELECT * FROM User WHERE user_name = ? OR email = ?",
                (username, email)
            )
        return len(cursor.fetchall()) > 0

def get_user(username: str) -> Optional[Dict]:
    """Get user information from database"""
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE user_name = ?", (username,))
        result = cursor.fetchone()
        if result:
            return {"id": result[0], "username": result[1], "email": result[2]}
    return None

def is_user_signed_in() -> bool:
    """Check if user is signed in"""
    if session is not None:
        try:
            return session.get("user_email") is not None
        except KeyError:
            pass
    return False

# Route handlers with direct database operations
@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index_page():
    """The index page"""
    if is_user_signed_in():
        return redirect("/dashboard")
    return redirect("/signin")

@app.route("/registration", methods=['GET', 'POST'])
def registration_page():
    """The registration page"""
    registration_data = render_template("registration.html")

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            with sqlite3.connect(USERS_DB) as conn:
                cursor = conn.cursor()
                if not check_account_exists(username, email):
                    hashed_password = encrypt_password(password)
                    cursor.execute(
                        "INSERT INTO User (user_name, email, hashed_password) VALUES (?, ?, ?)",
                        (username, email, hashed_password)
                    )
                    conn.commit()
                    return redirect("/dashboard")
                else:
                    registration_data += '<script>alert("Could not create account, possibly exists already")</script>\n'
        except sqlite3.Error:
            registration_data += '<script>alert("Could not create account")</script>\n'

    return registration_data

@app.route("/signin", methods=['GET', 'POST'])
def signin_page():
    """The signin page"""
    signin_data = render_template("signin.html")

    if request.method == "POST":
        user_name_email = request.form["name_email"]
        password = request.form["password"]

        if check_account_exists(user_name_email, user_name_email, password):
            user = get_user(user_name_email)
            if user:
                session["user_id"] = user["id"]
                session["user_name"] = user["username"]
                session["user_email"] = user["email"]
                signin_data += '<script>alert("Signed in successfully!");window.location.href="/dashboard";</script>'
        else:
            signin_data += '<script>alert("Could not sign in, either email/username or password are incorrect");</script>'

    return signin_data

@app.route("/dashboard", methods=['GET'])
def dashboard_page():
    """The dashboard page"""
    if not is_user_signed_in():
        return redirect("/index")
    return render_template("dashboard.html")

@app.route("/books", methods=['GET'])
def books_page():
    """The books page"""
    if not is_user_signed_in():
        return redirect("/")
    return render_template("books.html")

@app.route("/description", methods=['GET'])
def description_page():
    """The book description page"""
    if not is_user_signed_in():
        return redirect("/")

    description_data = render_template("description.html")
    if request.method == "GET":
        book_id = request.args.get("book_id", "")
        if book_id:
            description_data = description_data.replace("BOOKID", book_id)

    return description_data

@app.route("/logoff", methods=['GET'])
def logoff_page():
    """Log off the user"""
    session.clear()
    return "<script>alert('Logged off successfully');window.location.href='/signin';</script>"

@app.route("/wishlist", methods=['GET'])
def read_wishlist():
    """Get user's wishlist"""
    if not is_user_signed_in():
        return redirect("/")

    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_id FROM Wishlist WHERE account_id = ?", (session["user_id"],))
        wishlist = cursor.fetchall()
        
    data = ""
    for wishlist_ids in wishlist:
        index = wishlist.index(wishlist_ids)
        for book_id in wishlist_ids:
            if index < (len(wishlist) - 1):
                data += f"{book_id}, "
            else:
                data += f"{book_id}"
    return data

@app.route("/book", methods=['GET'])
def get_books():
    """Get book information"""
    if not is_user_signed_in():
        return redirect("/")

    response = "No book found"
    if request.method == "GET":
        book_id = request.args.get("id", "")
        if book_id != "":
            book_id = int(book_id)
            if book_id == 0:
                book_id += 1

            with sqlite3.connect(BOOKS_DB) as conn:
                cursor = conn.cursor()
                if book_id >= 1:
                    cursor.execute("SELECT * FROM Book WHERE id = ?", (book_id,))
                    result = cursor.fetchone()
                    if result:
                        response = json.dumps({
                            "id": result[0],
                            "title": result[1],
                            "author": result[2],
                            "rating": float(result[3])
                        })
                else:
                    cursor.execute("SELECT * FROM Book")
                    books = cursor.fetchall()
                    response = json.dumps([{
                        "id": book[0],
                        "title": book[1],
                        "author": book[2],
                        "rating": float(book[3])
                    } for book in books]) if books else "[]"
    return response

@app.route("/add", methods=['POST', 'GET'])
def add_page():
    """Add books, reviews, or wishlist items"""
    if not is_user_signed_in():
        return redirect("/")

    add_type = request.args.get("type", "")
    results = ""

    if add_type == "book":
        title = request.form["title"]
        author = request.form["author"]
        
        with sqlite3.connect(BOOKS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Book WHERE title = ? AND author = ?", (title, author))
            if cursor.fetchone():
                results += "<script>alert('Failed to add book, already exists');history.go(-1);</script>"
            else:
                cursor.execute(
                    "INSERT INTO Book (title, author, rating_avg) VALUES (?, ?, ?)",
                    (title, author, 0)
                )
                conn.commit()
                results += "<script>alert('Added book successfully');history.go(-1);</script>"

    elif add_type == "wishlist":
        book_id = request.args["book_id"]
        account_id = session["user_id"]
        
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Wishlist WHERE account_id = ? AND book_id = ?",
                (account_id, book_id)
            )
            if cursor.fetchone():
                results += "<script>alert('Failed to add to wishlist');history.go(-1);</script>"
            else:
                cursor.execute(
                    "INSERT INTO Wishlist (account_id, book_id) VALUES (?, ?)",
                    (account_id, book_id)
                )
                conn.commit()
                results += "<script>alert('Added to wishlist!');history.go(-1);</script>"

    elif add_type == "review":
        account_id = session["user_id"]
        book_id = request.args["book_id"]
        review_title = request.form["review_title"]
        review_text = request.form["review_text"]
        rating = request.form["rating"]
        
        with sqlite3.connect(BOOKS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM Review 
                WHERE account_id = ? AND book_id = ? AND rating_score = ? 
                AND review_title = ? AND review_text = ?""",
                (account_id, book_id, rating, review_title, review_text)
            )
            if cursor.fetchone():
                results += "<script>alert('Could not add review, possibly already added');history.go(-1);</script>"
            else:
                cursor.execute(
                    """INSERT INTO Review 
                    (account_id, book_id, rating_score, review_title, review_text)
                    VALUES (?, ?, ?, ?, ?)""",
                    (account_id, book_id, rating, review_title, review_text)
                )
                conn.commit()
                results += "<script>alert('Review added successfully.');history.go(-1);</script>"

    return results

@app.route("/get", methods=['GET'])
def get_page():
    """Get reviews"""
    if not is_user_signed_in():
        return redirect("/")

    type_get = request.args["type"]
    book_id = request.args["book_id"]

    with sqlite3.connect(BOOKS_DB) as conn:
        cursor = conn.cursor()
        if type_get == "user":
            cursor.execute(
                "SELECT * FROM Review WHERE account_id = ? AND book_id = ?",
                (session["user_id"], book_id)
            )
            review = cursor.fetchone()
            if review:
                return json.dumps({
                    "account_id": review[1],
                    "book_id": review[2],
                    "rating_score": float(review[3]),
                    "review_title": review[4],
                    "review_text": review[5]
                })
        elif type_get == "all":
            cursor.execute("SELECT * FROM Review WHERE book_id = ?", (book_id,))
            reviews = cursor.fetchall()
            if reviews:
                return json.dumps([{
                    "account_id": review[1],
                    "book_id": review[2],
                    "rating_score": float(review[3]),
                    "review_title": review[4],
                    "review_text": review[5]
                } for review in reviews])

    return "[]"

if __name__ == "__main__":
    app.run(debug=False)