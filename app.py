#imports

import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from pathlib import Path

env_path = Path(__file__).parent / ".env"
print("Looking for .env at:", env_path, "| exists:", env_path.exists())
load_dotenv(env_path)
print("DB_USER:", os.getenv("DB_USER"), "| DB_NAME:", os.getenv("DB_NAME"))

app = Flask(__name__) # App

# Connects to the database by name, user, password, host, and port from a .env file
def connect_database():
    try:
        connection = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME"),
            port = int(os.getenv("DB_PORT", 3306))
        )

        # means connection succesful
        return connection 
    except mysql.connector.Error as e:
        # return nothing if failed to connect
        print("Database connection failed:", e)
        return None

#main page
@app.route("/")
def home():
    conn = connect_database() # Connect database

    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True) # Allows to return query results
    cursor.execute("SELECT * FROM assignments ORDER BY due_date") # Selects everything from assignments ordered by due date
    assignments = cursor.fetchall() # Gets each record

    # Close cursor and connection
    cursor.close()
    conn.close()

    today = datetime.now() # Current date today
    completed = [a for a in assignments if a["complete"]] # Looks for completed assignments
    past_due = [a for a in assignments if a["due_date"] < today and not a["complete"]] # Looks for past-due assignments that are past due
    upcoming = [a for a in assignments if a["due_date"] >= today and not a["complete"]] # Looks for uncomplete assignments 
    
    
    return render_template("index.html", assignments=assignments, past_due=past_due, upcoming=upcoming, completed=completed)

# Navigate to addStudents.html
@app.route("/add-student", methods=["GET", "POST"])
def addStudentPage():
    if request.method == "GET":
        return render_template("addStudent.html")

    
    subject = request.form["subject"].strip() # Assignment subject
    title = request.form["title"].strip() # Assignment title
    desc = request.form["desc"].strip() # Assignment desc

    # Assignment due date
    # Try/catch statement to check for validity

    # Try to get datetime
    try:
        due = get_datetime()
        

    # Error for invalid date    
    except ValueError:
        return render_template("addStudent.html", error= "Invalid date or time."), 400

    # Actally adds assignment to the database
    execute_query(
                        "INSERT INTO assignments (assignment_subject, title, assignment_desc, due_date)" "VALUES (%s, %s, %s, %s)",
                        subject, title, desc, due
                     )

    # Redirect back to main page after
    return redirect(url_for("home"))

# deletes an assignment from the database
@app.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
def delete_assignment(assignment_id):
    execute_query("DELETE FROM assignments WHERE assignment_id = %s", assignment_id)
    return redirect(url_for("home"))

# Sets an assignment as complete when users presses complete button for an assignment
@app.route("/assignments/<int:assignment_id>/complete", methods=["POST"])
def complete_assignment(assignment_id):
    execute_query("UPDATE assignments SET complete = 1 WHERE assignment_id = %s ", assignment_id)
    return redirect(url_for("home"))

# Sets an assignment as uncomplete when users presses uncomplete button for an assignment
@app.route("/assignments/<int:assignment_id>/uncompleteBtn", methods=["POST"])
def uncomplete_assignment(assignment_id):
    execute_query("UPDATE assignments SET complete = 0 WHERE assignment_id = %s ", assignment_id)
    return redirect(url_for("home"))


@app.route("/update-student/<int:assignment_id>", methods=["GET", "POST"])
def updateStudentPage(assignment_id):
    assignment = get_assignment(assignment_id)

    if request.method == "GET":
        due = assignment["due_date"]
        # Gets properties of a selected assignmen, then display them for each input box
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

    subject = request.form["subject"].strip() # Assignment subject
    title = request.form["title"].strip() #Assignment  title
    desc = request.form["desc"].strip() # Assignment description
    
    # Try to get datetime
    try:
       due = get_datetime()
        
    except ValueError:
        return render_template("updateStudent.html", error= "Invalid date or time."), 400
    
    # Actually edit the student in database
    execute_query(
                        "UPDATE assignments SET assignment_subject = %s, title = %s, assignment_desc = %s, due_date = %s WHERE assignment_id = %s",
                        subject, title, desc, due, assignment_id
                        )

    # Redirect back to main page after
    return redirect(url_for("home"))

# Function to prevent repetition, and save lines of code
def execute_query(query, *args):
    conn = connect_database()

    if conn is None:
        raise RuntimeError("Failed to connect database")
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, args) # Executes the query and with the properites if any
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback() # Rollback if any errors
        raise
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

# Gets the datetime
def get_datetime():
    am_or_pm = request.form["AMorPM"].strip() # AM or PM
    month = int(request.form["month"]) # Month 
    day = int(request.form["day"]) # Day
    year = int(request.form["year"]) # Year
    hour = int(request.form["hour"]) #Hour
    minute = int(request.form["minute"]) # Minute

    # Hour is out of range of hour isn't between 1 and 12
    if not 1 <= hour <= 12:
        raise ValueError("Hour out of range")

    # Adds 12 if it's pm (only allows military time)
    hour24 = hour % 12 + (12 if am_or_pm == "PM" else 0)

    # Full datetime
    return datetime(year, month, day, hour24, minute)


# Gets properties of an assignment by selected id
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

# Puts dur date in an AM-PM format instead of showing it in military time
@app.template_filter("format_due")
def format_due(value):
    hour = value.hour % 12 or 12
    am_pm = "PM" if value.hour >= 12 else "AM"
    return f"{value.strftime('%b %d, %Y')} {hour}:{value.minute:02d} {am_pm}"

# actually runs the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)