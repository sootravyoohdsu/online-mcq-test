from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "msmaths_secret_key"

DATABASE = "database.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    option1 TEXT,
                    option2 TEXT,
                    option3 TEXT,
                    option4 TEXT,
                    correct_option TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT,
                    score INTEGER,
                    submitted_at TEXT
                )''')

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/start", methods=["POST"])
def start():
    roll = request.form["roll"]
    session["roll"] = roll

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")
    questions = c.fetchall()
    conn.close()

    return render_template("exam.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    score = 0

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM questions")
    all_questions = c.fetchall()

    for q in all_questions:
        qid = str(q[0])
        selected = request.form.get(qid)
        correct = q[6]

        if selected == correct:
            score += 1

    roll = session.get("roll")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("INSERT INTO results (roll_no, score, submitted_at) VALUES (?, ?, ?)",
              (roll, score, now))

    conn.commit()
    conn.close()

    return render_template("result.html", score=score)

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM results")
    results = c.fetchall()
    conn.close()
    return render_template("admin.html", results=results)

if __name__ == "__main__":
    app.run()

