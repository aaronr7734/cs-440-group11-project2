import os
from flask import Flask

class Wrapper:
    def __init__(self, name):
        self.__app = Flask(name)
        self.__app.secret_key = "BooksListSecretKey"
        self.__routes = {}
    
    """Assigns a function to a given route"""
    def add_route(self, route, func):
        self.__routes[route] = func
        self.__app.add_url_rule(route, methods=["post", "get"], view_func=func)
    
    """Runs the flask web server"""
    def run(self, *args, **kwargs):
        self.__app.run(*args, **kwargs)

    """Adds a specified route for files with a specific prefix"""
    def add_all(self, folder_path: str, prefix: str, func):
        #Get all items in folder
        items = os.listdir(folder_path)
        #Go through all items and add them
        for item in items:
            #Get the item path
            item_path = "{}/{}".format(folder_path, item)
            if(os.path.isdir(item_path)):
                #Is a directory, recurse through
                self.add_all(item_path, prefix, func)
            else:
                #Check if the name contains our prefix
                item_prefix = item.split(".")
                item_prefix = item_prefix[len(item_prefix) - 1]
                if(item_prefix in prefix):
                    #Add the path as a route to our function
                    self.add_route("/{}".format(item_path), func)

    """Returns content from file"""
    def content(self, file_name: str):
        #Open the file for reading
        with open(file_name, "r") as file:
            #Read the lines from the file
            return file.readlines()

    """Returns the flask instance"""
    def app(self):
        return self.__app