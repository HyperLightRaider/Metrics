import sqlite3
from datetime import date
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_PATH = "states.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT UNIQUE,
            sleep INTEGER,
            energy INTEGER,
            mood INTEGER,
            productivity INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/save", methods=["POST"])
def save_state():
    data = request.get_json()
    today = date.today().isoformat()

    sleep = int(data.get("sleep", 5))
    energy = int(data.get("energy", 5))
    mood = int(data.get("mood", 5))
    productivity = int(data.get("productivity", 5))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # проверяем, есть ли запись за сегодня
    cur.execute("SELECT id FROM states WHERE day = ?", (today,))
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE states
            SET sleep = ?, energy = ?, mood = ?, productivity = ?
            WHERE day = ?
            """,
            (sleep, energy, mood, productivity, today),
        )
    else:
        cur.execute(
            """
            INSERT INTO states (day, sleep, energy, mood, productivity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (today, sleep, energy, mood, productivity),
        )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "message": "Состояние сохранено"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
