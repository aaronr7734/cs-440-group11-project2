from user.user import User
from book.book import Book
from flask import request, redirect, session
from web.wrapper import Wrapper
import sys

#Create a server wrapper to allow interacting with database
server = Wrapper(__name__)

"""The main registration page"""
def registration_page():
    #Create / open accounts and books
    user = User("resources/database/accounts.db")
    #The registration page data
    registration_data = "\n".join(server.content("resources/web/registration.html"))
    #Check if the user submit their registration data
    if(request.method == "POST"):
        #Get the username
        username = request.form["username"]
        #And the email
        email = request.form["email"]
        #And the password
        password = request.form["password"]
        #Now, try to create an account
        if(user.register(username, email, password)):
            #Made the account, redirect to dashboard
            return redirect("/dashboard")
        else:
            #Could not make account
            registration_data += '<script>alert("Could not create account, possibly exists already")</script>\n'
    
    #Close the account
    user.close()
    #Read the registration html page
    return registration_data

"""The dashboard page (consists of wishlist and list of books)"""
def dashboard_page():
    #And get the dashboard page's data
    dashboard_data = "\n".join(server.content("resources/web/dashboard.html"))

    #Check if the user is signed in
    if(session != None):
        try:
            if(session["user_email"] == None):
                #User is not signed in
                return redirect("/index")
        except KeyError:
            return redirect("/index")
    
    return dashboard_data

"""The main sign in page"""
def signin_page():
    #Create / open accounts database
    user = User("resources/database/accounts.db")
    #The sign in page's data
    signin_data = "\n".join(server.content("resources/web/signin.html"))
    #Check if we should sign in
    if(request.method == "POST"):
        #We should sign the user in, get the name/email and password
        user_name_email = request.form["name_email"]
        password = request.form["password"]
        #And check if they exist
        if(user.account_exists(user_name_email, user_name_email, password = password)):
            #Search for the user id, name, and email using password
            password = user.encrypt(password)
            user_data = user.db().select("User", where = "(`user_name` = \"{}\" OR `email`=\"{}\") AND `hashed_password`=\"{}\"".format(user_name_email, user_name_email, password))
            user_id = user_data[0][0]
            user_name = user_data[0][1]
            user_email = user_data[0][2]
            
            #Now add all to your session data
            session["user_id"] = user_id
            session["user_name"] = user_name
            session["user_email"] = user_email

            #Notify that user was signed in
            signin_data += '<script>alert("Signed in successfully!");window.location.href="/dashboard";</script>'
        else:
            #Could not sign in
            signin_data += '<script>alert("Could not sign in, either email/username or password are incorrect");</script>'
    #Close the account
    user.close()
    #And return the signin page data
    return signin_data

"""The index page"""
def index_page():
    #Check if the user has signed in
    if(session != None):
        try:
            if(session["user_email"] != None):
                #Signed in, display the dashboard
                return redirect("/dashboard")
        except KeyError:
            #Redirect to sign in
            return redirect("/signin")
    #Not signed in or session not set, redirect to sign in page
    return redirect("/signin")


"""The default function for all CSS files"""
def read_css_data():
    #Get the requested CSS file and read its content
    css_file = request.url.replace(request.url_root, "")
    return "\n".join(server.content(css_file))

"""Non-page, returns string containing user's wishlist"""
def read_wishlist():
    #Create / open accounts database
    users = User("resources/database/accounts.db")
    #Now check if the user has signed in
    if(session != None):
        try:
            if(session["user_email"] != None):
                #User has signed in, return the wishlist
                data = ""
                wishlist = users.get_wishlist(session["user_id"])
                #Convert the wishlist into a comma-separated string
                for wishlist_ids in wishlist:
                    index = wishlist.index(wishlist_ids)
                    for id in wishlist_ids:
                        if(index < (len(wishlist) - 1)):
                            data += "{}, ".format(id)
                        else:
                            data += "{}".format(id)
                #And return it
                return data
        except KeyError:
            pass
    #Close the database
    users.close()
    #Redirect to main page
    return redirect("/")

"""Returns if a user is signed in"""
def is_signed_in():
    #Check if a session has been initialized
    if(session != None):
        try:
            #Determine if a user signed in using the email
            return (session["user_email"] != None)
        except KeyError as e:
            pass
    #User has not signed in
    return False

        

"""Non-page, gets book data based on id. If id < 0, it returns a list of books."""
def get_books():
    #Create / open books database
    books = Book("resources/database/books.db")
    response = "No book found";

    #Check if user has not signed in
    if(not is_signed_in()):
        #Not signed in, redirect to index
        return redirect("/")

    #Check if the user has sent a GET request
    if(request.method == "GET"):
        book_id = request.args["id"]
        #Make sure ID is not empty
        if(book_id != ""):
            book_id = int(book_id)
            #Check if book id is 0
            if(book_id == 0):
                book_id += 1
            #Check if book id is valid
            if(book_id >= 1):
                #Return the book's information
                response = str(books.get_book(book_id))
            else:
                #Return a list of all books
                response = str(books.get_books())
    return response

"""The books page, full of all books"""
def books_page():
    #Read books page
    books_data = "\n".join(server.content("resources/web/books.html"))
    #And return the books page
    return books_data

"""The description page, contains reviews, title, and author"""
def description_page():
    #Create / open accounts and books databases
    users = User("resources/database/accounts.db")
    books = Book("resources/database/books.db")
    description_data = "\n".join(server.content("resources/web/description.html"))
    #Check if the description page received GET
    if(request.method == "GET"):
        #Check if the user has signed in
        if(session != None):
            try:
                if(session["user_email"] != None):
                    #Signed in, get account and book id
                    book_id = request.args["book_id"]
                    description_data = description_data.replace("BOOKID", book_id)
            except KeyError:
                #Redirect to index page
                return redirect("/")
    #Finally, return the description page
    return description_data

"""Logs the user off"""
def logoff_page():
    #Reset the session
    session.clear()
    return "<script>alert('Logged off successfully');history.go(-1);</script>";

"""Adds either a book or a review"""
def add_page():
    #Create / open books and accounts database
    books = Book("resources/database/books.db")
    users = User("resources/database/accounts.db")
    #Get what should be added (book, review, etc)
    add_type = request.args["type"]
    results = ""
    #Check if we should add a book, book to wishlist, or a review
    if(add_type == "book"):
        #Get the title and the author
        title = request.form["title"]
        author = request.form["author"]

        #And add the book to our database, if we can
        if(books.add_book(title, author, 0)):
            results += "<script>alert('Added book successfully');history.go(-1);</script>"
        else:
            results += "<script>alert('Failed to add book, already exists');history.go(-1);</script>"
    #Check if we are adding a book to our wishlist
    elif(add_type == "wishlist"):
        #Get the book and account ID
        book_id = request.args["book_id"]
        account_id = session["user_id"]

        book_id = str(book_id)
        account_id = str(account_id)
        #Now try to add the book to our wishlist
        if(not users.add_wishlist(account_id, book_id)):
            #Failed to add book to wishlist
            results += "<script>alert('Failed to add to wishlist');history.go(-1);</script>"
        else:
            #Added to wishlist
            results += "<script>alert('Added to wishlist!');history.go(-1);</script>"
    #Check if we should add a review
    elif(add_type == "review"):
        account_id = session["user_id"]
        book_id = request.args["book_id"]
        review_title = request.form["review_title"]
        review_text = request.form["review_text"]
        rating = request.form["rating"]
        
        #Try to add the review
        if(books.add_review(account_id, book_id, rating, review_title, review_text)):
            results += "<script>alert('Review added successfully.');history.go(-1);</script>"
        else:
            results += "<script>alert('Could not add review, possibly already added');history.go(-1);</script>"
    return results

"""Page for getting review"""
def get_page():
    #Type to get (single review, all reviews)
    type_get = request.args["type"]
    #Gets all review data associated with book id
    book_id = request.args["book_id"]
    #Create / open books database
    books = Book("resources/database/books.db")
    #Check if we should get a user's review
    if(type_get == "user"):
        #And get all reviews associated with book id and user
        return str(books.get_review(session["user_id"], book_id))
    elif(type_get == "all"):
        #Get all reviews associated with book
        return str(books.get_reviews(book_id))


"""The main program"""
def main(server: Wrapper, args):
    #Add the main pages to our wrapper
        #Add the wishlist page
    server.add_route("/wishlist", read_wishlist)
        #And the book and review adding page
    server.add_route("/add", add_page)
        #And the review getting page, for API
    server.add_route("/get", get_page)
        #And the book page
    server.add_route("/book", get_books)
        #And the books page
    server.add_route("/books", books_page)
        #Now add a logoff page
    server.add_route("/logoff", logoff_page)
        #And the registration page
    server.add_route("/registration", registration_page)
        #And the sign in page
    server.add_route("/signin", signin_page)
        #And the dashboard
    server.add_route("/dashboard", dashboard_page)
        #Now add the description page
    server.add_route("/description", description_page)
        #And the index page
    server.add_route("/", index_page)
    server.add_route("/index", index_page)
        #Now add all css and js files
    server.add_all("resources/web", ".css", read_css_data)
    server.add_all("resources/web", ".js", read_css_data)
    #Run the server
    server.run()
if(__name__ == "__main__"):
    main(server, sys.argv)