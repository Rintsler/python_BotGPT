import datetime
import sqlite3
from datetime import datetime, timedelta
import openai
import traceback
import time
import schedule
from threading import Thread


def handle_rate_limit_error(api_key, chat_history, user_id, message):
    user_id = message.from_user.id  # Обратите внимание, что вы уже определили user_id в функции
    dbkey_connection = sqlite3.connect('keys.db')
    dbkey_cursor = dbkey_connection.cursor()

    dbkey_cursor.execute('UPDATE info_key SET status_key=2 WHERE api_key=?', (api_key,))
    dbkey_connection.commit()
    dbkey_connection.close()
    print("Пытаюсь отправить второй раз")
    api_key = get_unused_key()
    print("Пытаюсь отправить второй раз2")
    while not api_key:
        # print("Нет свободных ключей")
        time.sleep(10)
        api_key = get_unused_key()
    try:
        update_key_status(api_key, 1)
        print("Пытаюсь отправить второй раз3")
        system_message = {"role": "system", "content": "You are a helpful assistant"}
        messages = [system_message] + chat_history[-5:]  # Передаем последние два сообщения
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            api_key=api_key,
            messages=messages,
            temperature=0.8,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        otvet = response['choices'][0]['message']['content'].strip()
        print("Пытаюсь отправить второй раз")
        tokens_used = len(otvet)
        print(tokens_used)
        # Обновляем столбец tokens_used в базе данных
        conn_tok = sqlite3.connect("users.db")
        cursor_tok = conn_tok.cursor()
        cursor_tok.execute('''
            UPDATE users
            SET tokens_used = tokens_used + ?
            WHERE user_id = ?
        ''', (tokens_used, user_id))
        print("записвыаю")
        conn_tok.commit()
        conn_tok.close()
        reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        log_error(api_key, error_text)
        return handle_rate_limit_error(api_key, chat_history, user_id, message)


def update_expired_keys():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    try:
        # Получаем все ключи со статусом 2 и временем последнего изменения статуса более 1 минуты назад
        cursor.execute(
            'SELECT * FROM info_key WHERE status_key=2 AND (julianday("now") - julianday(status_change)) * 24 * 60 > 1')
        expired_keys = cursor.fetchall()

        for key in expired_keys:
            # Устанавливаем статус ключа в 0
            cursor.execute('UPDATE info_key SET status_key=0 WHERE api_key=?', (key[1],))
            print(f"Key {key[1]} status updated to 0")
        conn.commit()

    finally:
        conn.close()


def update_days_keys():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    try:
        # Получаем все ключи со статусом 3 и временем последнего изменения статуса более 24 часов назад
        cursor.execute(
            'SELECT * FROM info_key WHERE status_key=3 AND (julianday("now") - julianday(status_change)) * 24 > 24')
        expired_keys = cursor.fetchall()

        for key in expired_keys:
            # Устанавливаем статус ключа в 0
            cursor.execute('UPDATE info_key SET status_key=0, requests_day_key = 0 WHERE api_key=?', (key[1],))
            print(f"Key {key[1]} status updated to 0")
        conn.commit()

    finally:
        conn.close()


def update_one_keys():
    conn_one_keys = sqlite3.connect('keys.db')
    cursor_one_keys = conn_one_keys.cursor()
    try:
        # Получаем все ключи со статусом 1 и временем последнего изменения более 2 минут назад
        three_minutes_ago = datetime.now() - timedelta(minutes=3)
        cursor_one_keys.execute(
            'SELECT * FROM info_key WHERE status_key=1 AND status_change < ?', (three_minutes_ago,))
        expir_keys = cursor_one_keys.fetchall()

        for key in expir_keys:
            # Устанавливаем статус ключа в 0
            cursor_one_keys.execute('UPDATE info_key SET status_key=0 WHERE api_key=?', (key[1],))
            print(f"Key {key[1]} status updated to 0")
        conn_one_keys.commit()

    finally:
        conn_one_keys.close()


def schedule_thread():
    # Создаем объект schedule
    sched = schedule.Scheduler()

    # Добавляем задачу в расписание
    sched.every(1).minutes.do(update_expired_keys)
    sched.every(24).hours.do(update_days_keys)
    sched.every(1).minutes.do(update_one_keys)
    while True:
        sched.run_pending()
        time.sleep(1)


# Запуск расписания в отдельном потоке
schedule_thread = Thread(target=schedule_thread)
schedule_thread.start()


def get_unused_key():
    conn_search = sqlite3.connect('keys.db')
    cursor_search = conn_search.cursor()

    try:
        while True:
            cursor_search.execute('SELECT * FROM info_key WHERE status_key=0 AND where_use="chat" LIMIT 1')
            unused_key_info = cursor_search.fetchone()

            if unused_key_info:
                if unused_key_info[5] == 200:
                    cursor_search.execute(
                        'UPDATE info_key SET status_key=3, status_change=datetime("now") WHERE api_key=?',
                        (unused_key_info[1],))
                    conn_search.commit()
                else:
                    return unused_key_info[1]  # Возвращаем API ключ

            print("Нет доступных ключей или запросов недостаточно, ожидание...")
            time.sleep(10)

    finally:
        conn_search.close()


def log_error(api_key, error_text):
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()

    try:
        # Обновляем значение status_error
        cursor.execute('UPDATE info_key SET status_error=? WHERE api_key=?', (error_text, api_key))
        conn.commit()

    except sqlite3.Error as e:
        # Обработка ошибок при взаимодействии с базой данных
        print(f"Ошибка при обновлении статуса ошибки: {e}")

    finally:
        conn.close()


def update_key_status(api_key, status):
    conn_update = sqlite3.connect('keys.db')
    cursor_update = conn_update.cursor()
    cursor_update.execute('UPDATE info_key SET status_key=?, status_change=datetime("now") WHERE api_key=?',
                          (status, api_key))
    cursor_update.execute('UPDATE info_key SET requests_day_key = COALESCE(requests_day_key, 0) + 1 WHERE api_key=?',
                          (api_key,))
    conn_update.commit()
    conn_update.close()


def reset_key_status(api_key):
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()

    try:
        # Обновляем значение status_key на 0
        cursor.execute('UPDATE info_key SET status_key=0,status_change=datetime("now") WHERE api_key=?', (api_key,))
        conn.commit()
    finally:
        conn.close()
