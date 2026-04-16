import sqlite3
import os

# Получаем абсолютный путь к директории, где находится этот скрипт
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Жестко связываем имя файла с этой директорией
DB_PATH = os.path.join(BASE_DIR, 'health_navigator.db')

def get_db_connection():
    """Создает и возвращает подключение к базе данных SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализирует таблицы базы данных, если они не существуют."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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

    cursor.execute("SELECT id FROM users WHERE username = 'TestUser'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username) VALUES ('TestUser')")

    conn.commit()
    conn.close()
    print(f"База данных успешно инициализирована по пути: {DB_PATH}")