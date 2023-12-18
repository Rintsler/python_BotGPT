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

# функции для сохранения и получения истории сообщений ____________________________________________________________________
def save_message(user_id, message_text):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (user_id, message_text) VALUES (?, ?)', (user_id, message_text))
    conn.commit()
    conn.close()


def get_message_history(user_id):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('SELECT message_text FROM messages WHERE user_id = ? ORDER BY rowid DESC LIMIT 5', (user_id,))
    history = cursor.fetchall()
    conn.close()
    return [message[0] for message in history]
# ________________________________________________________________________________________________________________________
