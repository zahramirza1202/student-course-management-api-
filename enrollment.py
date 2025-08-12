import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # your MySQL password if any
        database="studentDB"
    )