import sqlite3
import os

DB_PATH = 'health_navigator.db'

def get_db_connection():
    """Создает и возвращает подключение к базе данных SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Позволяет обращаться к столбцам по именам (как к словарям)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализирует таблицы базы данных, если они не существуют."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица дневника самочувствия
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mood_score INTEGER CHECK(mood_score >= 1 AND mood_score <= 5),
            symptoms_text TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица объективных метрик (носимые устройства)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_type TEXT NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Создаем тестового пользователя для MVP, если его еще нет
    cursor.execute("SELECT id FROM users WHERE username = 'TestUser'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username) VALUES ('TestUser')")

    conn.commit()
    conn.close()
    print("База данных успешно инициализирована.")