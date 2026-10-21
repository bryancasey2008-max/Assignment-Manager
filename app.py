import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect, url_for
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
    cursor.execute("SELECT * FROM assignments ORDER BY due_date")
    assignments = cursor.fetchall()
    
    cursor.close()
    conn.close()

    today = datetime.now()
    past_due = [a for a in assignments if a["due_date"] < today]
    upcoming = [a for a in assignments if a["due_date"] >= today]
    
    
    return render_template("index.html", assignments=assignments, past_due=past_due, upcoming=upcoming)

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

    execute_database(
                        "INSERT INTO assignments (assignment_subject, title, assignment_desc, due_date)" "VALUES (%s, %s, %s, %s)",
                        subject, title, desc, due
                     )

    return redirect(url_for("home"))

@app.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
def delete_assignment(assignment_id):
    print(assignment_id)
    execute_database("DELETE FROM assignments WHERE assignment_id = %s", assignment_id)
    return redirect(url_for("home"))

@app.route("/update-student/<int:assignment_id>", methods=["GET", "POST"])
def updateStudentPage(assignment_id):
    assignment = get_assignment(assignment_id)

    if request.method == "GET":
        due = assignment["due_date"]

        form = {
            "subject": assignment["assignment_subject"],
            "title": assignment["title"],
            "desc": assignment["assignment_desc"],
            "month": due.month,
            "day": due.day,
            "year": due.year,
            "hour": due.hour % 12 or 12,
            "minute": due.minute,
            "AMorPM": "PM" if due.hour >= 12 else "AM"
        }
        return render_template("updateStudent.html", assignment=assignment, form=form)

def execute_database(query, *args):
    conn = connect_database()
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        return render_template("index.html", error= f"Database error {e}"), 500
    finally:
        cursor.close()
        conn.close()

def get_assignment(assignment_id):
    conn = connect_database()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM assignments WHERE assignment_id = %s", (assignment_id,))
        return cursor.fetchone()
    except mysql.connector.Error as e:
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    app.run()

connection.close()