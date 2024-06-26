import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

def init_db():
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        correct_name TEXT NOT NULL,
                        correct_aquarium TEXT NOT NULL,
                        guessed_name TEXT NOT NULL,
                        guessed_aquarium TEXT NOT NULL,
                        name_result INTEGER NOT NULL,
                        aquarium_result INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    db.create_all()

def save_result(username, correct_name, correct_aquarium, guessed_name, guessed_aquarium, name_result, aquarium_result):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO results (username, correct_name, correct_aquarium, guessed_name, guessed_aquarium, name_result, aquarium_result)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (username, correct_name, correct_aquarium, guessed_name, guessed_aquarium, int(name_result), int(aquarium_result)))
    conn.commit()
    conn.close()

def get_all_results(username=None):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    if username:
        cursor.execute('SELECT username, correct_name, correct_aquarium, guessed_name, guessed_aquarium, name_result, aquarium_result, timestamp FROM results WHERE username = ?', (username,))
    else:
        cursor.execute('SELECT username, correct_name, correct_aquarium, guessed_name, guessed_aquarium, name_result, aquarium_result, timestamp FROM results')
    results = cursor.fetchall()
    conn.close()
    return results
