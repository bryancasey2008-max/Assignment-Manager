import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, render_template

connection = None
app = Flask(__name__)
app.debug = True

# We do not want to hardcode any sensitive information
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
    conn = connect_database()

    if conn is None:
        print("Database not found")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM assignments")
    assignments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    
    return render_template("index.html", assignments=assignments)

@app.route("/add-student", methods = ["GET", "POST"])
def addStudentPage():
    return render_template("addStudent.html")

if __name__ == "__main__":
    connection = connect_database()
    debug = True
    app.run()

connection.close()