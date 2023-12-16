# -*- coding: utf-8 -*-
from aiogram import types
import datetime
import sqlite3
from data.data_base import DB_PATH, cursor, conn, generate_response
from handlers import subscription_keyboard, menu_keyboard

from loader import dp



# Обработчик для кнопки "💰 Подписка"
@dp.message_handler(lambda message: message.text == "💰 Подписка")
async def send_subscription_menu(message: types.Message):
    text = "Выберите тип подписки:"
    await message.answer(text, reply_markup=subscription_keyboard)


# Обработчик для выбора подписки
@dp.message_handler(lambda message: message.text in ["Старт", "Комфорт", "Профи"])
async def handle_subscription_choice(message: types.Message):
    user_id = message.from_user.id
    subscribe_type = message.text
    sub_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Определение количества токенов в зависимости от выбранной подписки
    if subscribe_type == "Старт":
        tokens = 10000
    elif subscribe_type == "Комфорт":
        tokens = 50000
    elif subscribe_type == "Профи":
        tokens = 100000
    else:
        # Если подписка не распознана, обработайте это по вашему усмотрению
        tokens = 0
    # Здесь вам нужно выполнить запись в базу данных
    # Например:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET subscribe = ?, sub_date = ?, tokens = ? 
        WHERE user_id = ?
    ''', (subscribe_type, sub_date, tokens, user_id))
    conn.commit()

    response_text = f'Вы выбрали подписку тариф {subscribe_type}. Вам доступно {tokens} токенов. Спасибо!'
    await message.answer(response_text, reply_markup=menu_keyboard)


@dp.message_handler(lambda message: message.text == "📝 Токены")
async def show_tokens(message: types.Message):
    user_id = message.from_user.id

    # Замените "your_table_name" на фактическое имя вашей таблицы в базе данных
    cursor.execute('SELECT subscribe, tokens, tokens_used FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        subscribe_type, total_tokens, tokens_used = user_data
        remaining_tokens = total_tokens - tokens_used

        response_text = (
            f'Общее количество токенов по подписке "{subscribe_type}": {total_tokens}\n'
            f'\nОставшееся количество токенов: {remaining_tokens}'
        )
    else:
        response_text = "Пользователь не найден в базе данных."

    await message.answer(response_text, reply_markup=menu_keyboard)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    text = (
        "Привет! Я твой телеграм-бот. Отправь мне свой вопрос, и я постараюсь ответить."
    )
    await message.answer(text, reply_markup=menu_keyboard)


@dp.message_handler(lambda message: message.text == "👤 Регистрация")
async def process_registration(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    registration_date = message.date

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        response_text = "Вы уже зарегистрированы."
    else:
        # Регистрируем нового пользователя
        cursor.execute('''
            INSERT INTO users (user_id, username, registration_date)
            VALUES (?, ?, ?)
        ''', (user_id, username, registration_date))
        conn.commit()
        response_text = "Регистрация успешна!"

    await message.answer(response_text, reply_markup=menu_keyboard)


@dp.message_handler()
async def process_question(message: types.Message):
    user_question = message.text
    print(f"User question: {user_question}")

    response = generate_response(user_question)
    print(f"OpenAI response: {response}")

    await message
