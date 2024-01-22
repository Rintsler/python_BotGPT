import datetime
import time
import traceback
from datetime import datetime, timedelta
import openai
from app.update_keys import get_unused_key, update_key_status, reset_key_status, log_error, set_key_status_to_2
from data.db_app import calculate_remaining_tokens, update_tokens_used


async def get_subscription_info(user_id, sub_date):
    remaining_tokens = await calculate_remaining_tokens(user_id)
    if sub_date:
        remaining_days = await calculate_remaining_days(sub_date)
        return {
            "remaining_tokens": remaining_tokens,
            "remaining_days": remaining_days
        }
    else:
        return {
            "remaining_tokens": 0,
            "remaining_days": 0
        }  # Если пользователь не найден, возвращаем 0


async def calculate_remaining_days(registration_date):
    try:
        db_datetime = datetime.strptime(registration_date, "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()

        # Рассчитываем разницу в днях
        remaining_days = (db_datetime + timedelta(days=30)) - current_date

        return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0

    except ValueError as e:
        print(f"Ошибка при преобразовании даты: {e}")
        return None


async def generate_response(user_id, chat_history, message):
    api_key = await get_unused_key()
    while not api_key:
        # print("Нет свободных ключей")
        time.sleep(10)
        api_key = await get_unused_key()
    try:
        await update_key_status(api_key, 1)

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
        await update_tokens_used(tokens_used, user_id)
        print("записвыаю")
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return handle_rate_limit_error(user_id, api_key, chat_history, message)


async def handle_rate_limit_error(user_id, api_key, chat_history, message):
    # dbkey_connection = sqlite3.connect('keys.db')
    # dbkey_cursor = dbkey_connection.cursor()
    # dbkey_cursor.execute('UPDATE info_key SET status_key=2 WHERE api_key=?', (api_key,))
    # dbkey_connection.commit()
    # dbkey_connection.close()
    await set_key_status_to_2(api_key)
    print("Пытаюсь отправить второй раз")
    api_key = await get_unused_key()
    print("Пытаюсь отправить второй раз2")
    while not api_key:
        # print("Нет свободных ключей")
        time.sleep(10)
        api_key = await get_unused_key()
    try:
        await update_key_status(api_key, 1)
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
        await update_tokens_used(tokens_used, user_id)
        print("записвыаю")
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return handle_rate_limit_error(user_id, api_key, chat_history, message)

