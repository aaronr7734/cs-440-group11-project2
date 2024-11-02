import hashlib
from db.db import Database

class User:
    def __init__(self, account_db_path: str):
        #Create a connection to our account database
        self.__db = Database(account_db_path)
        #And create the account and wishlist table
        self.__db.create_table("User", ["id", "user_name", "email", "hashed_password"], ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT"])
        self.__db.create_table("Wishlist", ["account_id", "book_id"], ["INTEGER REFERENCES User(id)", "INTEGER"])

    """Encrypts a text using SHA-256"""
    def encrypt(self, text: str):
        #Use SHA-256 encryption on text
        message = hashlib.sha256()
        message.update(text.encode())
        #Encrypt the text
        return message.hexdigest()

    """Creates an account if username and email are not in database"""
    def register(self, user_name, email, password):
        #Check if the account database contains the given username and email
        if(self.account_exists(user_name, email)):
            print("register(): account exists. Sign in, please.")
            return False
        #User does not exist, add the given information
        user_name = "\"{}\"".format(user_name)
        email = "\"{}\"".format(email)
            #Encrypt the password using SHA-256
        hashed_password = "\"{}\"".format(self.encrypt(password))
            #And try to add the user details to the account database
        account_cursor = self.__db.insert("User", ["NULL", user_name, email, hashed_password])
        added = account_cursor != None
        #Check if the user was not added
        if(not added):
            print("register(): failed to add account \"{}\"".format(user_name))
            return False
        return True

    """Returns if an account exists based on the username and email"""
    def account_exists(self, user_name, email, password: str = None):
        #Check if password is set
        if(password != None):
            #Encrypt the password
            password = self.encrypt(password)
            #And return if the account with the given password exists
            return (len(self.__db.select("User", where = "(`user_name` = \"{}\" OR `email`=\"{}\") AND `hashed_password`=\"{}\"".format(user_name, email, password))))
        #Looks for the username and email in the account database and returns if it exists
        return (len(self.__db.select("User", where = "`user_name` = \"{}\" OR `email` = \"{}\"".format(user_name, email)))) != 0

    """Adds book id to wishlist"""
    def add_wishlist(self, account_id: int, book_id: int):
        #Check if the book is already in wishlist
        book_exists = len(self.__db.select("Wishlist", where = "`account_id` = \"{}\" AND `book_id`=\"{}\"".format(account_id, book_id))) != 0
        if(book_exists):
            print("add_wishlist(): book already added to wishlist.")
            return False;
        #Add book to user's wishlist
        inserted = self.__db.insert("Wishlist", [account_id, book_id])
        if(not inserted):
            print("add_wishlist(): could not add book to wishlist.")
        return inserted

    """Get wishlist"""
    def get_wishlist(self, account_id: int):
        #Look for account id in wishlist database
        return self.__db.select("Wishlist", select_keys=["`book_id`"] , where="`account_id`={}".format(account_id))

    """Closes the database"""
    def close(self):
        #Close the database
        self.__db.close()
    

    """Returns current database instance"""
    def db(self):
        return self.__db