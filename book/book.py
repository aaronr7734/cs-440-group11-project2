from db.db import Database
import json

class Book:
    def __init__(self, book_db_path: str):
        #Connect to the book database
        self.__db = Database(book_db_path)
        #And create the book and review tables
        self.__db.create_table("Book", ["id", "title", "author", "rating_avg", ], ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "REAL"])
        self.__db.create_table("Review", ["review_id", "account_id", "book_id", "rating_score", "review_title", "review_text"], ["INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "INTEGER", "REAL", "TEXT", "TEXT"])
    
    # Checks if a book exists
    def book_exists(self, title: str, author: str):
        #Return if a book exists
        return (len(self.__db.select("Book", where = "`title` = {} AND `author` = {}".format(title, author)))) != 0
    
    """Adds book to book database"""
    def add_book(self, title: str, author: str, avg_rating: float):
        #Insert book details to the book database
            #String format the parameters
        title = "\"{}\"".format(title)
        author = "\"{}\"".format(author)
        avg_rating = "\"{}\"".format(avg_rating)
            #Make sure the book was not already added
        if(self.book_exists(title, author)):
            #Book exists, no need to add it
            print("add_book(): \"{}\" by \"{}\" was already added.".format(title, author))
            return False
        book_added = self.__db.insert("Book", ["NULL", title, author, avg_rating])
            #Check if book was not added
        if(not book_added):
            #Book was not added for some reason
            print("add_book(): failed to add book \"{}\" by \"{}\"".format(title, author))
            return False
        print("add_book(): Book was added successfully.")
        #Book was added
        return True
    
    """Checks if a review is already added"""
    def review_exists(self, account_id: int, book_id: int, rating_score: float, review_title: str, review_text: str):
        #Returns if a given review exists
        where_stmt = "`account_id` = {} AND `book_id`={} AND `rating_score` = {} AND `review_title`={} AND `review_text`={}"
        where_stmt = where_stmt.format(account_id, book_id, rating_score, review_title, review_text)
        return (len(self.__db.select("Review", where = where_stmt))) != 0

    """Adds review to book review database"""
    def add_review(self, account_id: int, book_id: int, rating_score: float, review_title: str, review_text: str):
        #Insert review details to the review database
            #Format the parameters
        account_id = "\"{}\"".format(account_id)
        book_id = "\"{}\"".format(book_id)
        rating_score = "\"{}\"".format(rating_score)
        review_title = "\"{}\"".format(review_title)
        review_text = "\"{}\"".format(review_text)
        #Make sure the review was not already added
        if(self.review_exists(account_id, book_id, rating_score, review_title, review_text)):
            #Review exists
            print("add_review(): your review was already posted.")
            return False
        #Try to add the review
        review_added = self.__db.insert("Review", ["NULL", account_id, book_id, rating_score, review_title, review_text])
        if(not review_added):
            print("add_review(): failed to add review to book.")
            return False
        return True

    """Gets book based on book id"""
    def get_book(self, id: int):
        #Check if the book exists
        book_data = self.__db.select("Book", where = "`id` = {}".format(id))
        if(len(book_data) != 0):
            #Dictionary for json
            data = dict()
            #Get book data as json
            for book in book_data:
                #Get the book id, title, author, and rating
                book_id = book[0]
                title = book[1]
                author = book[2]
                #And add them to the dictionary
                data["id"] = book_id
                data["title"] = title
                data["author"] = author
            #Return the data as json
            return json.dumps(data)
        return None
    
    """Gets all books in database"""
    def get_books(self):
        #Go through all books
        books = self.db().select("Book", where = "1=1")
        #Check if books have been added already
        if(len(books) != 0):
            #Books have been added, get all of their data
            data = list()
            data_idx = 0
            #Get all books and their data
            for book in books:
                #Get book id, title, author, and rating
                book_id = book[0]
                title = book[1]
                author = book[2]
                rating = float(book[3])
                #Add the book data to data list
                data.append(dict())
                data[data_idx]["id"] = book_id
                data[data_idx]["title"] = title
                data[data_idx]["author"] = author
                data[data_idx]["rating"] = rating

                #Append data index
                data_idx += 1
            #Now convert the data dictionary to json
            return json.dumps(data)
        #No books found
        return None
    
    """Gets review based on account and book id"""
    def get_review(self, account_id: int, book_id: int):
        #Find all book reviews with this data
        reviews = self.__db.select("Review", where="`account_id`={} AND `book_id`={}".format(account_id, book_id))
        #Check if the review was found
        if(len(reviews) != 0):
            data = dict()
            #Go through all reviews
            for review in reviews:
                #Get the rating score, title, and text
                rating_score = review[3]
                review_title = review[4]
                review_text = review[5]
                #And add it to data dictionary
                data["account_id"] = account_id
                data["book_id"] = book_id
                data["rating_score"] = rating_score
                data["review_title"] = review_title
                data["review_text"] = review_text
            #And return as JSON
            return json.dumps(data)
        #Return nothing
        return None
    
    """Gets all reviews for a book"""
    def get_reviews(self, book_id: int):
        #Find all book reviews with this data
        reviews = self.__db.select("Review", where="`book_id`={}".format(book_id))
        #Check if the review was found
        if(len(reviews) != 0):
            #Create a list for reviews
            data = list()
            data_idx = 0;
            #Go through all reviews
            for review in reviews:
                #Get the rating score, title, and text
                account_id = review[1]
                rating_score = review[3]
                review_title = review[4]
                review_text = review[5]
                
                #And add it to data dictionary
                data.append(dict())
                data[data_idx]["account_id"] = account_id
                data[data_idx]["book_id"] = book_id
                data[data_idx]["rating_score"] = rating_score
                data[data_idx]["review_title"] = review_title
                data[data_idx]["review_text"] = review_text

                #Now increment the index
                data_idx += 1
            #And return as JSON
            return json.dumps(data)
        #Return nothing
        return None
    

    """Updates a book based on its ID"""
    def update_book(self, book_id: int, title: str, author: str, rating: float):
        #Check if the book does not exist
        if(not self.book_exists(title, author)):
            #The book does not exist
            return False
        #Try to update the book
        return self.__db.update("Book", ["title", "author", "rating_avg"], [title, author, rating], whereStmt="`book_id`={}".format(book_id))
    
    """Updates a rating based on book and account id"""
    def update_rating(self, account_id: int, book_id: int, rating_score: int, review_title: str, review_text: str):
        #Check if the rating does not exist
        if(not self.review_exists(account_id, book_id, rating_score, review_title, review_text)):
            return False
        #Try to update the rating
        return self.__db.update("Review", ["account_id", "book_id", "rating_score", "review_title", "review_text"],
                                [account_id, book_id, rating_score, review_title, review_text],
                                whereStmt="`account_id`={} AND `book_id`={}".format(account_id, book_id))

    """Gets the database"""
    def db(self):
        return self.__db

    """Closes the current book database"""
    def close(self):
        #Close our book database
        self.__db.close()