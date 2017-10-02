import sqlite3
from flask import g
import datetime

import os
DATABASE = '52CO.sqlite'


# Connect to the database.
def connect_db():
    db_path = os.path.join(os.getcwd(), DATABASE)
    if not os.path.isfile(db_path):
        raise RuntimeError("Can't find database file '{}'".format(db_path))
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


# Open a database connection and hang on to it in the global object.
def open_db_connection():
    g.db = connect_db()


# If the database is open, close it.
def close_db_connection():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Convert the 'row' retrieved with 'cursor' to a dictionary
# whose keys are column names and whose values are column values.
def row_to_dictionary(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary

######################################


# all available jobs
def jobs():
    print("jobs")
    return g.db.execute('SELECT * FROM job').fetchall()
