#imports
import sqlite3
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__) # App

# The database is a single file stored next to app.py (no server, no password)
DB_PATH = Path(__file__).parent / "assignments.db"


# Connects to the SQLite database file
def connect_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Lets us read columns by name
    return conn


# Creates the table the first time the app runs (replaces schema.sql)
def init_db():
    conn = connect_database()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                assignment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                title              TEXT NOT NULL,
                assignment_desc    TEXT NOT NULL,
                assignment_subject TEXT NOT NULL,
                due_date           TEXT NOT NULL,
                complete           INTEGER NOT NULL DEFAULT 0,
                created            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()

init_db()


# Turns a database row into a dictionary and converts due_date text back into a datetime
def row_to_dict(row):
    data = dict(row)
    data["due_date"] = datetime.fromisoformat(data["due_date"])
    return data


#main page
@app.route("/")
def home():
    conn = connect_database()
    try:
        rows = conn.execute("SELECT * FROM assignments ORDER BY due_date").fetchall()
    finally:
        conn.close()

    assignments = [row_to_dict(r) for r in rows]

    today = datetime.now() # Current date today
    completed = [a for a in assignments if a["complete"]] # Completed assignments
    past_due = [a for a in assignments if a["due_date"] < today and not a["complete"]] # Past-due assignments
    upcoming = [a for a in assignments if a["due_date"] >= today and not a["complete"]] # Uncompleted assignments

    return render_template("index.html", assignments=assignments, past_due=past_due, upcoming=upcoming, completed=completed)


# Navigate to addStudent.html
@app.route("/add-student", methods=["GET", "POST"])
def addStudentPage():
    if request.method == "GET":
        return render_template("addStudent.html")

    subject = request.form["subject"].strip() # Assignment subject
    title = request.form["title"].strip() # Assignment title
    desc = request.form["desc"].strip() # Assignment desc

    # Try to get datetime
    try:
        due = get_datetime()
    except ValueError:
        return render_template("addStudent.html", error="Invalid date or time."), 400

    # Actually adds assignment to the database
    execute_query(
        "INSERT INTO assignments (assignment_subject, title, assignment_desc, due_date) VALUES (?, ?, ?, ?)",
        subject, title, desc, due.strftime("%Y-%m-%d %H:%M:%S")
    )

    # Redirect back to main page after
    return redirect(url_for("home"))


# Deletes an assignment from the database
@app.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
def delete_assignment(assignment_id):
    execute_query("DELETE FROM assignments WHERE assignment_id = ?", assignment_id)
    return redirect(url_for("home"))


# Sets an assignment as complete
@app.route("/assignments/<int:assignment_id>/complete", methods=["POST"])
def complete_assignment(assignment_id):
    execute_query("UPDATE assignments SET complete = 1 WHERE assignment_id = ?", assignment_id)
    return redirect(url_for("home"))


# Sets an assignment as uncomplete
@app.route("/assignments/<int:assignment_id>/uncompleteBtn", methods=["POST"])
def uncomplete_assignment(assignment_id):
    execute_query("UPDATE assignments SET complete = 0 WHERE assignment_id = ?", assignment_id)
    return redirect(url_for("home"))


@app.route("/update-student/<int:assignment_id>", methods=["GET", "POST"])
def updateStudentPage(assignment_id):
    assignment = get_assignment(assignment_id)

    if assignment is None:
        abort(404)

    if request.method == "GET":
        due = assignment["due_date"]
        # Gets properties of the selected assignment, then displays them in each input box
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
    title = request.form["title"].strip() # Assignment title
    desc = request.form["desc"].strip() # Assignment description

    # Try to get datetime
    try:
        due = get_datetime()
    except ValueError:
        return render_template("updateStudent.html", assignment=assignment, form=request.form, error="Invalid date or time."), 400

    # Actually edit the assignment in the database
    execute_query(
        "UPDATE assignments SET assignment_subject = ?, title = ?, assignment_desc = ?, due_date = ? WHERE assignment_id = ?",
        subject, title, desc, due.strftime("%Y-%m-%d %H:%M:%S"), assignment_id
    )

    # Redirect back to main page after
    return redirect(url_for("home"))


# Function to prevent repetition, and save lines of code
def execute_query(query, *args):
    conn = connect_database()
    try:
        conn.execute(query, args) # Executes the query with the values, if any
        conn.commit()
    except sqlite3.Error:
        conn.rollback() # Rollback if any errors
        raise
    finally:
        conn.close()


# Gets the datetime from the form (12-hour input converted to 24-hour)
def get_datetime():
    am_or_pm = request.form["AMorPM"].strip().upper() # AM or PM
    month = int(request.form["month"]) # Month
    day = int(request.form["day"]) # Day
    year = int(request.form["year"]) # Year
    hour = int(request.form["hour"]) # Hour
    minute = int(request.form["minute"]) # Minute

    # Hour must be between 1 and 12
    if not 1 <= hour <= 12:
        raise ValueError("Hour out of range")

    if am_or_pm not in ("AM", "PM"):
        raise ValueError("Must be AM or PM")

    # Adds 12 if it's PM
    hour24 = hour % 12 + (12 if am_or_pm == "PM" else 0)

    # Full datetime (raises ValueError for impossible dates)
    return datetime(year, month, day, hour24, minute)


# Gets properties of an assignment by selected id
def get_assignment(assignment_id):
    conn = connect_database()
    try:
        row = conn.execute("SELECT * FROM assignments WHERE assignment_id = ?", (assignment_id,)).fetchone()
    finally:
        conn.close()
    return row_to_dict(row) if row else None


# Puts due date in an AM-PM format instead of showing it in military time
@app.template_filter("format_due")
def format_due(value):
    hour = value.hour % 12 or 12
    am_pm = "PM" if value.hour >= 12 else "AM"
    return f"{value.strftime('%b %d, %Y')} {hour}:{value.minute:02d} {am_pm}"


# Actually runs the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)