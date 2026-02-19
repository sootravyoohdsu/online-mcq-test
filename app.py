from flask import Flask, render_template, request, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "msmaths_secret_key")

# Render requires proper writable path
DATABASE = os.path.join(os.getcwd(), "database.db")

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
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
    roll = request.form.get("roll")
    session["roll"] = roll

    conn = get_connection()
    questions = conn.execute(
        "SELECT * FROM questions ORDER BY RANDOM() LIMIT 10"
    ).fetchall()
    conn.close()

    return render_template("exam.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    conn = get_connection()
    questions = conn.execute("SELECT * FROM questions").fetchall()

    score = 0
    for q in questions:
        selected = request.form.get(str(q["id"]))
        if selected == q["correct_option"]:
            score += 1

    roll = session.get("roll")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        "INSERT INTO results (roll_no, score, submitted_at) VALUES (?, ?, ?)",
        (roll, score, now),
    )
    conn.commit()
    conn.close()

    return render_template("result.html", score=score)

@app.route("/admin")
def admin():
    conn = get_connection()
    results = conn.execute("SELECT * FROM results").fetchall()
    conn.close()
    return render_template("admin.html", results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
