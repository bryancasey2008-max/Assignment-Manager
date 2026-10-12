import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask

connection = None
app = Flask(__name__)

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

@app.route("/")
def home():
    return "<h1>Hello World</h1>"

if __name__ == "__main__":
    connection = connect_database()
    app.run()

connection.close()