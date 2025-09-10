# src/db_connection.py
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",  # Replace with your MySQL root password
        database="fletapp"
    )
