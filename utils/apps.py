import datetime
import sqlite3
from datetime import datetime, timedelta
import openai
from data.data_base import cursor
import traceback
import time
from utils.update_keys import get_unused_key, update_key_status, reset_key_status, log_error, handle_rate_limit_error


def get_user_balance(user_id):
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def get_subscription_info(user_id):
    cursor.execute('SELECT tokens, tokens_used, registration_date FROM users WHERE user_id = ?', (user_id,))
    tokens, tokens_used, registration_date = cursor.fetchone()
    remaining_tokens = tokens - tokens_used  # Перемещено сюда, после присвоения значений переменным
    if registration_date:
        remaining_days = calculate_remaining_days(registration_date)
        return {
            "tokens": tokens,
            "tokens_used": tokens_used,
            "remaining_tokens": remaining_tokens,
            "remaining_days": remaining_days
        }
    else:
        return {
            "tokens": 0,
            "tokens_used": 0,
            "remaining_tokens": 0,
            "remaining_days": 0
        }  # Если пользователь не найден, возвращаем 0


def calculate_remaining_days(registration_date):
    # Преобразуем строку с датой регистрации в объект db_datetime
    db_datetime = datetime.strptime(registration_date, "%Y-%m-%d %H:%M:%S")

    # Получаем текущую дату и время
    current_date = datetime.now()

    # Рассчитываем разницу в днях
    remaining_days = (db_datetime + timedelta(days=30)) - current_date

    return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0


def get_free_request(user_id):
    cursor.execute('SELECT free_request FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def free_req_true(user_id):
    cursor.execute('SELECT flag FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def get_subscription(user_id):
    cursor.execute('SELECT subscribe FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result


def get_user(user_id):
    cursor.execute('SELECT user_id, flag FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        user, flag = result
        return user


def get_subscription_date(user_id):
    cursor.execute('SELECT sub_date FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def generate_response(chat_history, user_id, message):
    api_key = get_unused_key()
    while not api_key:
        # print("Нет свободных ключей")
        time.sleep(10)
        api_key = get_unused_key()
    try:
        update_key_status(api_key, 1)

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


def calculate_remaining_tokens(user_id):
    cursor.execute('SELECT tokens, tokens_used FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        tokens, tokens_used = user_data
        remaining_tokens = tokens - tokens_used
        return remaining_tokens
    else:
        # Если пользователя с указанным user_id нет в базе данных
        return None
