from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll_number TEXT,
            email TEXT,
            department TEXT,
            year_sem TEXT,
            club TEXT,
            feedback TEXT,
            sentiment TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    text = data.get("feedback", "")
    sentiment = TextBlob(text).sentiment.polarity
    sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO feedback (name, roll_number, email, department, year_sem, club, feedback, sentiment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("name"), data.get("rollNumber"), data.get("email"),
        data.get("department"), data.get("yearSem"),
        data.get("club"), data.get("feedback"), sentiment_label
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Feedback submitted successfully", "sentiment": sentiment_label})
@app.route('/')
def home():
    return 'Backend is running!'

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (data['username'], data['password']))
        conn.commit()
        return jsonify({"message": "Signup successful"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (data['username'], data['password']))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run()