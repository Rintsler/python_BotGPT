import datetime
import sqlite3
from datetime import datetime, timedelta
import openai
from data.data_base import cursor
from aiogram.dispatcher.filters.state import State, StatesGroup


# Состояние
class UserStates(StatesGroup):
    FIRST_MESSAGE = State()


def get_user_balance(user_id):
    # Замените 'ваша_таблица_user_balance' на реальное имя таблицы в вашей базе данных
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def get_subscription_info(user_id):
    # Замените 'вашатаблица_subscription_info' на реальное имя таблицы в вашей базе данных
    cursor.execute('SELECT tokens, tokens_used, registration_date FROM users WHERE user_id = ?',
                   (user_id,))
    result = cursor.fetchone()
    if result:
        tokens, tokens_used, registration_date = result
        remaining_tokens = tokens - tokens_used  # Перемещено сюда, после присвоения значений переменным
        remaining_days = calculate_remaining_days(registration_date)
        return {
            "tokens": tokens,
            "tokens_used": tokens_used,
            "remaining_tokens": remaining_tokens,
            "remaining_days": remaining_days
        }
    else:
        return {"tokens": 0, "tokens_used": 0, "remaining_tokens": 0,
                "remaining_days": 0}  # Если пользователь не найден, возвращаем 0


def calculate_remaining_days(registration_date):
    # Преобразуем строку с датой регистрации в объект db_datetime
    db_datetime = datetime.strptime(registration_date, "%Y-%m-%d %H:%M:%S")

    # Получаем текущую дату и время
    current_date = datetime.now()

    # Рассчитываем разницу в днях
    remaining_days = (db_datetime + timedelta(days=30)) - current_date

    return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0


def get_subscription(user_id):
    # Замените 'ваша_таблица_subscription_info' на реальное имя таблицы в вашей базе данных
    cursor.execute('SELECT subscribe FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def get_user(user_id):
    # Замените 'ваша_таблица_subscription_info' на реальное имя таблицы в вашей базе данных
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    print("user_id: ", result)
    return result


def get_subscription_date(user_id):
    # Замените 'ваша_таблица_subscription_info' на реальное имя таблицы в вашей базе данных
    cursor.execute('SELECT sub_date FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Если пользователь не найден, возвращаем 0


def generate_response(chat_history, user_id):
    get_user(user_id)
    system_message = {"role": "system", "content": "You are a helpful assistant"}
    messages = [system_message] + chat_history[-5:]  # Передаем последние два сообщения
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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
    return otvet


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
