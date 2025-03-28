import sqlite3
from datetime import datetime

DB_NAME = "plankibot.db"

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            status TEXT,
            initial_time INTEGER,
            current_time INTEGER,
            days INTEGER,
            misses INTEGER,
            join_date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name TEXT,
            members TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username, plank_time):
    """Добавление нового пользователя"""
    conn = sqlite3.connect("plankibot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, username, status, initial_time, current_time, days, misses, join_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, "active", plank_time, plank_time, 0, 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user(user_id):
    """Получение данных пользователя"""
    conn = sqlite3.connect("plankibot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_misses(user_id, misses):
    """Обновление количества пропусков пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET misses = ? WHERE id = ?", (misses, user_id))
    conn.commit()
    conn.close()

user_id = 123456789  # Укажите реальный ID пользователя
user = get_user(user_id)
print(f"Полученные данные пользователя: {user}")