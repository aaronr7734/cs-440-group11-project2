import os
import sqlite3

class Database:

    """Creates / opens an sqlite database"""
    def __init__(self, db_path: str):
        #Build this database instance
        self.__build_db(db_path)
    
    """Builds a database instance"""
    def __build_db(self, db_path: str):
        #Connect to the database
        self.__db_path = db_path
        try:
            self.__db = sqlite3.connect(self.__db_path)
            self.__cursor = self.__db.cursor()
        except sqlite3.OperationalError:
            #Error encountered while connecting, possible not in existing directory
            #Get the parent directory of the database
            parent = os.path.abspath(os.path.join(self.__db_path, os.pardir))
            if(not os.path.exists(parent)):
                #Create the given path
                os.makedirs(parent)
                print("Database(): could not open \"{}\" since \"{}\" did not exist. Running this code again.".format(self.__db_path, parent))
                #Build this database again
                self.__build_db(db_path)

    """Creates a new table"""
    def create_table(self, table_name: str, keys: list, key_types: list):
        #Exit if keys and types size mismatch
        if(len(keys) != len(key_types)):
            print("create_table(): mismatched sizes between keys and key types")
            return False
        #Create the sql command
        command = "CREATE TABLE IF NOT EXISTS {} (".format(table_name)
        for key_idx in range(0, len(keys)):
            key = keys[key_idx]
            key_type = key_types[key_idx]
            command += "{} {}".format(key, key_type)
            if(key_idx < (len(keys) - 1)):
                command += ","
            else:
                command += ")".format(key, key_types)
        #And execute it
        create_cursor = self.__cursor.execute(command)
        #And return if the sql code was executed
        return create_cursor != None
    
    """Inserts values into table given table name and keys"""
    def insert(self, table_name: str, values: list):
        #Create a command for inserting values
        command = "INSERT INTO {} VALUES ({})".format(table_name, ", ".join(values))
        #Now execute it
        insert_cursor = self.__cursor.execute(command)
        inserted = (insert_cursor != None)
        #And commit the changes
        self.__db.commit()
        return inserted
    
    """Updates values present in table based on where"""
    def update(self, table_name: str, keys: list, values: list, whereStmt: str = None):
        #Check if keys and values mismatch
        if(len(keys) != len(values)):
            print("update(): keys and values sizes mismatch.")
            return False
        
        #Create a command for updating
        command = "UPDATE {} SET ".format(table_name)
        for index in range(len(keys)):
            key = keys[index]
            value = values[index]
            command += "{}={}".format(key, value)
            if(index < (len(keys) - 1)):
                command += ", "
        #Check if the where statement was set
        if(whereStmt != None):
            command += " WHERE ({})".format(whereStmt)
        
        #Now execute that command
        update_cursor = self.__db.execute(command)
        updated = (update_cursor != None)

        #And commit the changes
        self.__db.commit()
        return updated

    """Gets value associated with key from table"""
    def select(self, table_name: str, select_keys: list = ["*"], where = None):
        #Create a command for selecting values
        command = "SELECT {} FROM {} ".format(", ".join(select_keys), table_name)
        if(where != None):
            command += "WHERE ({})".format(where)
        #Now execute it and get all values
        select_cursor = self.__cursor.execute(command)
        return select_cursor.fetchall()
    
    """Commits changes to database and closes connections to it"""
    def close(self):
        #Commit all changes and close connections
        self.__db.commit()
        self.__cursor.close()
        self.__db.close()