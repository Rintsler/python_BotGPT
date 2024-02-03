import datetime
import time
import traceback
from datetime import datetime, timedelta
import openai
from aiogram.types import LabeledPrice
from app.update_keys import get_unused_key, update_key_status, reset_key_status, log_error, set_key_status_to_2
from data.config import bot, YOOTOKEN
from data.db_app import calculate_remaining_tokens, update_tokens_used, get_user_data
from data.metadata import Metadata
from nav.keyboard import inline_kb_pay


async def calculate_remaining_days(sub_date, flag):
    try:
        db_datetime = datetime.strptime(sub_date, "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()
        # Рассчитываем разницу в днях
        if flag == 3:
            remaining_days = (db_datetime + timedelta(days=30)) - current_date
            return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0
        if flag == 4:
            remaining_days = (db_datetime + timedelta(days=180)) - current_date
            return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0
        if flag == 5:
            remaining_days = (db_datetime + timedelta(days=365)) - current_date
            return max(remaining_days.days, 0)  # Возвращаем оставшееся количество дней, но не меньше 0
    except ValueError as e:
        print(f"Ошибка при преобразовании даты: {e}")
        return None


async def generate_response(user_id, chat_history, message):
    api_key = await get_unused_key()
    while not api_key:
        print("Нет свободных ключей")
        time.sleep(10)
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
        tokens_used = len(otvet)
        print("tokens_used: ", tokens_used)
        # Обновляем столбец tokens_used в базе данных
        await update_tokens_used(tokens_used, user_id)
        print("Обновляем столбец tokens_used в базе данных")
        await calculate_remaining_tokens(user_id)
        print("Обновляем столбец remaining_tokens в базе данных")
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return handle_rate_limit_error(user_id, api_key, chat_history, message)


async def handle_rate_limit_error(user_id, api_key, chat_history, message):
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
        # Обновляем столбец tokens_used в базе данных
        await update_tokens_used(tokens_used, user_id)
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return handle_rate_limit_error(user_id, api_key, chat_history, message)


async def profile(user_id):
    subscribe = ''
    pk, state_ai, user_id, flag, username, registration_date, chat_history, response_history, request, request_img, \
        tokens_used, sub_date, remaining_days, remaining_tokens = await get_user_data(user_id)
    user_info = [pk, user_id, flag, username, registration_date, chat_history, response_history, request, request_img,
                 tokens_used, sub_date, remaining_days, remaining_tokens]
    if sub_date:
        remaining_days = await calculate_remaining_days(sub_date, flag)

    for i in user_info:
        if i is None:
            i = ''
    if flag == 3:
        subscribe = "1 месяц"
        remaining_tokens = "действует подписка"
    elif flag == 4:
        subscribe = "6 месяцев"
        remaining_tokens = "действует подписка"
    elif flag == 5:
        subscribe = "1 год"
        remaining_tokens = "действует подписка"

    profile_text = (
        f"\t📊 Ваш профиль:\n"
        f"👤 Ваш ID: {user_id}\n"
        f"✅ Подписка: {subscribe}\n"
        f"📕 Остаток токенов: {remaining_tokens}\n"
        f"⏳ Дата регистрации: {registration_date}\n"
        f"🗓 Осталось дней подписки: {remaining_days}\n"
    )
    return profile_text


async def Subscribe():
    subscribe_text = (
        'Хочешь дальше общаться с ботом IZI, выбери подходящий себе тариф 👇\n\n'
        '⭐️ Тариф Light:'
        '\n\n'
        '⭐️ Тариф Middle:'
        '\n\n'
        '⭐️ Тариф Premium:'
        '\n\n'
        '☺️Каждый тариф можно оформить на разные периоды 🗓'
    )
    return subscribe_text


async def counting_pay(factor, description, user_id, sub_sum=0):
    if Metadata.subscription in 'Подписка Light':
        sub_sum = 10000 * factor
    elif Metadata.subscription in 'Подписка Middle':
        sub_sum = 35000 * factor
    elif Metadata.subscription in 'Подписка Full':
        sub_sum = 60000 * factor
    await bot.send_invoice(
        chat_id=user_id,
        title='Квитанция к оплате за подписку',
        description=description,
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[LabeledPrice(label=Metadata.subscription, amount=sub_sum)],
        max_tip_amount=30000,
        suggested_tip_amounts=[5000, 10000, 15000, 20000],
        start_parameter='test_bot',
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
