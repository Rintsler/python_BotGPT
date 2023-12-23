import json
from aiogram.dispatcher import FSMContext
from aiogram import types
from data.config import bot, dp
from data.data_base import DB_PATH, conn
from handlers.keyboard import subscription_keyboard, menu_keyboard
from utils.apps import *


@dp.message_handler(lambda message: message.text == "📊 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id

    # Получаем информацию о пользователе
    cursor.execute('SELECT user_id, registration_date FROM users WHERE user_id = ?', (user_id,))
    user_info = cursor.fetchone()

    if user_info:
        user_id, registration_date = user_info
        balance = get_user_balance(user_id)  # Функция для получения баланса пользователя
        subscription_info = get_subscription_info(user_id)  # Функция для получения информации о подписке пользователя
        subscription = get_subscription(user_id)
        sub_date = get_subscription_date(user_id)

        profile_text = (
            f"📊 Ваш профиль:\n"
            f"👤 Ваш айди: {user_id}\n"
            f"💰 Баланс: {balance} ₽\n"
            f"✅ Подписка: {subscription}\n"
            f"📕 Остаток токенов по подписке: {subscription_info['remaining_tokens']}\n"
            f"⏳ Дата регистрации: {registration_date}\n"
            f"🗓 Осталось дней подписки: {subscription_info['remaining_days']}\n"

            f"\nЕжедневно потраченные 10000 токенов возвращаются"
        )

        await message.answer(profile_text, reply_markup=menu_keyboard)
    else:
        await message.answer("Вы не зарегистрированы. Используйте кнопку '👤 Регистрация'.")


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


@dp.message_handler(lambda message: message.text == "📝 Токены")
async def show_tokens(message: types.Message):
    user_id = message.from_user.id

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


@dp.message_handler(lambda message: message.text == "👥 Создать чат")
async def create_chat(message: types.Message):
    user_id = message.from_user.id

    # Создаем новый чат для пользователя
    cursor.execute('''
        UPDATE users
        SET chat_history = ?,
            response_history = ?
        WHERE user_id = ?
    ''', ('[]', '[]', user_id))  # Обнуляем историю чата
    conn.commit()

    await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)


@dp.message_handler()
async def process_question(message: types.Message,state: FSMContext):
    user_state = await state.get_state()
    user_id = message.from_user.id
    user = get_user(user_id)
    # Если первое сообщение от пользователя
    if user_state is None:
        # Проверяем есть ли пользователь в базе
        if user:
            user_question = message.text
            print(f"User question: {user_question}")

            # Отправляем анимацию перед запросом к OpenAI GPT
            processing_message = await message.answer("🔄 Обработка запроса...")

            # Получаем текущую историю пользователя
            cursor.execute('SELECT chat_history, response_history FROM users WHERE user_id = ?', (user_id,))
            user_history, response_history = cursor.fetchone()
            user_history = json.loads(user_history) if user_history else []
            response_history = json.loads(response_history) if response_history else []

            # Добавляем новое сообщение к истории
            user_history.append({"role": "user", "content": user_question})

            # Обновляем историю в базе данных
            cursor.execute('''
                UPDATE users
                SET chat_history = ?,
                    response_history = ?
                WHERE user_id = ?
            ''', (
            json.dumps(user_history, ensure_ascii=False), json.dumps(response_history, ensure_ascii=False), user_id))
            conn.commit()

            # Имитация анимации перед запросом к OpenAI GPT завершена

            response = generate_response(user_history, user_id)
            print(f"OpenAI response: {response}")

            # Удаляем сообщение с анимацией перед отправкой ответа
            await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

            # Имитация анимации после получения ответа от OpenAI GPT
            await message.answer("✅ Готово!")

            # Добавляем ответ к истории ответов
            response_history.append({"role": "assistant", "content": response})
            cursor.execute('''
                UPDATE users
                SET response_history = ?
                WHERE user_id = ?
            ''', (json.dumps(response_history, ensure_ascii=False), user_id))
            conn.commit()
            # Запись состояния о первом сообщении
            await UserStates.FIRST_MESSAGE.set()
            await message.answer(response, reply_markup=menu_keyboard)
        else: await message.answer("Вам необходимо зарегистрироваться!")
