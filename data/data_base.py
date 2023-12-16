import sqlite3

# Установите путь к вашей базе данных SQLite
DB_PATH = 'users.db'
# Создаем подключение к базе данных
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Создаем таблицу пользователей, если ее нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        registration_date TEXT,
        tokens INTEGER,
        tokens_used INTEGER,
        subscribe INTEGER,
        sub_date TEXT
    )
''')
conn.commit()
