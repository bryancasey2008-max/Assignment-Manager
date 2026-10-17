import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect,  url_for, flash
from datetime import datetime

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

@app.route("/add-student", methods=["GET", "POST"])
def addStudentPage():
    if request.method == "GET":
        return render_template("addStudent.html")
    
    subject = request.form["subject"].strip()
    title = request.form["title"].strip()
    desc = request.form["desc"].strip()
    am_or_pm = request.form["AMorPM"].strip()


    try:

        month = int(request.form["month"])
        day = int(request.form["day"])
        year = int(request.form["year"])
        hour = int(request.form["hour"])
        minute = int(request.form["minute"])

        if not 1 <= hour <= 12:
            raise ValueError("Hour out of range")

        hour24 = hour % 12 + (12 if am_or_pm == "PM" else 0)
        due = datetime(year, month, day, hour24, minute)
        
    except ValueError:
        return render_template("addStudent.html", error= "Invalid date or time."), 400

    conn = connect_database()

    if conn is None:
        return render_template("addStudent.html", error= "Database not found"), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO assignments (assignment_subject, title, assignment_desc, due_date)" \
                        "values (%s, %s, %s, %s)",
                        (subject, title, desc, due),
                        )
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        return render_template("addStudent.html", error= f"Database error {e}"), 500
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("home"))

@app.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
def delete_assignment(assignment_id):
    print(assignment_id)

if __name__ == "__main__":
    app.run()

connection.close()