from .config import HOST, USER, PASSWORD, USER, DATABASE
from mysql.connector import Error
import mysql
from sqlalchemy import create_engine


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


engine = create_engine(
    f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")


def close_connection(connection):
    if connection:
        connection.close()
        print("Connection to MySQL DB closed")


def init():
    global conn
    conn = create_connection()


# initiate connection for the global variable
init()
