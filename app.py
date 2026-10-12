import mysql.connector
from dotenv import load_dotenv
import os

# We do not want to hardcode the username and password
load_dotenv()

def connect_database():
    try:
        connection = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME"),
            port = 3306
        )

        return connection
    except:
        return None

connection = connect_database()

if(connection != None):
    print("Database Connected")
else:
    print("Database not connected")

connection.close()