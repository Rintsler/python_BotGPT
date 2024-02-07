import datetime
import time
import traceback
import openai
from aiogram.types import LabeledPrice
from app.update_keys import get_unused_key, update_key_status, reset_key_status, log_error, set_key_status_to_2
from data.config import bot, YOOTOKEN
from data.db_app import get_user_data, update_requests
from data.metadata import Metadata
from nav.keyboard import inline_kb_pay
import sqlite3
import asyncio
from datetime import datetime, timedelta


async def update_tariffs_sub():
    # Подключаемся к базе данных
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    # Получаем текущую дату
    current_date = datetime.now()

    # Выполняем запрос для выборки данных
    cursor.execute('SELECT id, sub_date, period_sub, flag FROM users WHERE flag > 1')

    rows = cursor.fetchall()
    print("Проверяю базу")
    for row in rows:
        user_id, sub_date, period_sub, flag = row

        # Проверяем, что значение sub_date не является None перед преобразованием
        if sub_date:
            # Преобразуем строку в формат datetime с учетом миллисекунд
            sub_date = datetime.strptime(sub_date, '%Y-%m-%d %H:%M')

            # Проверяем условия для обновления
            if flag > 1:
                if period_sub == 1:
                    if (current_date - sub_date).days > 30:
                        cursor.execute('UPDATE users SET flag = 1, sub_date = ? WHERE id = ?', ('', user_id))
                elif period_sub == 6:
                    if (current_date - sub_date).days > 180:
                        cursor.execute('UPDATE users SET flag = 1, sub_date = ? WHERE id = ?', ('', user_id))
                elif period_sub == 12:
                    if (current_date - sub_date).days > 364:
                        cursor.execute('UPDATE users SET flag = 1, sub_date = ? WHERE id = ?', ('', user_id))

    # Сохраняем изменения и закрываем соединение
    print("Обновил подписки")
    connection.commit()
    connection.close()


async def scheduler():
    while True:
        await update_tariffs_sub()
        await asyncio.sleep(86400)


async def calculate_remaining_days(sub_date, flag):
    try:
        db_datetime = datetime.strptime(sub_date, "%Y-%m-%d %H:%M")
        current_date = datetime.now()
        # Рассчитываем разницу в днях
        if flag == 2:
            remaining_days = (db_datetime + timedelta(days=30)) - current_date
            return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0
        if flag == 3:
            remaining_days = (db_datetime + timedelta(days=180)) - current_date
            return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0
        if flag == 4:
            remaining_days = (db_datetime + timedelta(days=365)) - current_date
            return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0
    except ValueError as e:
        print(f"Ошибка при преобразовании даты: {e}")
        return None


async def generate_response(user_id, chat_history, message, request, request_img):
    api_key = await get_unused_key()
    while not api_key:
        print("Нет свободных ключей")
        await asyncio.sleep(10)
        api_key = await get_unused_key()
    try:
        await update_key_status(api_key, 1)

        system_message = {"role": "system", "content": "You are a helpful assistant"}
        messages = [system_message] + chat_history[-5:]  # Передаем последние два сообщения
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            api_key=api_key,
            messages=messages,
            temperature=0.8,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        otvet = response['choices'][0]['message']['content'].strip()
        print("Обновляем столбцы request, request_img в базе данных")
        await update_requests(user_id, request - 1, request_img)
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return handle_rate_limit_error(user_id, api_key, chat_history, message)


async def handle_rate_limit_error(user_id, api_key, chat_history, message, request, request_img):
    await set_key_status_to_2(api_key)
    print("Пытаюсь отправить второй раз")
    api_key = await get_unused_key()
    print("Пытаюсь отправить второй раз2")
    while not api_key:
        # print("Нет свободных ключей")
        await asyncio.sleep(10)
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
        # Обновляем столбец tokens_used в базе данных
        await update_requests(user_id, request, request_img)
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return handle_rate_limit_error(user_id, api_key, chat_history, message)


async def profile(user_id):
    subscribe = period = ''
    pk, state_ai, user_id, flag, username, registration_date, chat_history, response_history, request, request_img, \
        period_sub, sub_date, remaining_days = await get_user_data(user_id)
    user_info = [pk, user_id, flag, username, registration_date, chat_history, response_history, request, request_img,
                 period_sub, sub_date, remaining_days]
    if sub_date:
        remaining_days = await calculate_remaining_days(sub_date, flag)

    for i in user_info:
        if i is None:
            i = ''
    if flag == 2:
        subscribe = "Базовый"
    elif flag == 3:
        subscribe = "Расширенный"
    elif flag == 5:
        subscribe = "Премиум"

    if period_sub == 1:
        period = "Месяц"
    elif period_sub == 6:
        period = "6 месяцев"
    elif period_sub == 12:
        period = "Год"

    profile_text = (
        "📊 Ваш профиль\n\n"
        f"👤 Ваш ID: {user_id}\n\n"
        f"✅ Тариф: {subscribe}\n\n"
        f"📕 Период действия: {period}\n\n"
        f"⏳ Дата регистрации: {registration_date}\n\n"
        f"🗓 Осталось дней подписки: {remaining_days}\n"
    )
    return profile_text


async def Subscribe():
    subscribe_text = (
        'Хочешь дальше общаться с ботом Izi, выбери подходящий себе тариф 👇\n\n'
        '⭐️ Тариф Базовый:'
        '\n35 запросов в сутки - на ответы Izi в режиме текстового диалога'
        '\n15 запросов в сутки - Izi сгенерирует изображение по вашему запросу'
        '\n\n'
        '⭐️ Тариф Расширенный:'
        '\nбез ограничений - ответы Izi в режиме текстового диалога'
        '\n40 запросов в сутки - Izi сгенерирует изображение по вашему запросу'
        '\n\n'
        '⭐️ Тариф Премиум:'
        '\nПолный безлимит на все 😋\n\n'
        '☺️Каждый тариф можно оформить на разные периоды 🗓'
    )
    return subscribe_text


async def counting_pay(factor, user_id):
    sub_sum = Metadata.sub_sum * factor
    await bot.send_invoice(
        chat_id=user_id,
        title='Квитанция к оплате',
        description='Тариф',
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[LabeledPrice(label='Тариф ' + Metadata.subscription, amount=sub_sum)],
        max_tip_amount=1000000000,
        suggested_tip_amounts=[5000, 10000, 15000, 20000],
        start_parameter='Izi_bot',
        provider_data=None,
        # photo_url='https://i.ibb.co/zGw5X0B/image.jpg',
        # photo_size=100,
        # photo_width=800,
        # photo_height=450,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=inline_kb_pay,
        request_timeout=15
    )
