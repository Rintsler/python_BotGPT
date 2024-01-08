import json
import sqlite3
import datetime
import openai
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, LabeledPrice
from data.bufer import Buf
from data.config import bot, dp, YOOTOKEN
from data.data_base import DB_PATH, conn
from handlers.keyboard import menu_keyboard, inline_markup_submit, inline_markup_reg, menu_keyboard_free
from utils.apps import cursor, get_subscription_info, get_subscription_date, get_subscription, get_user, \
    get_user_balance, generate_response, get_free_request, free_req_true
from utils.update_keys import get_unused_key


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    text = (
        "Привет! Я ваш телеграм-бот. Отправь мне ваш вопрос, и я постараюсь ответить.\n\n"
        "У вас есть 5 бесплатных запросов к боту."
        "Для расширения функционала вам надо зарегистрироваться."
    )
    free_req = get_free_request(user_id)
    flag = free_req_true(user_id)
    if (free_req and flag) == 0:
        cursor.execute('''
                        INSERT INTO users_free (user_id, free_request, flag)
                        VALUES (?, ?, ?)
                    ''', (user_id, 5, 1))
        conn.commit()
        await message.answer(text, reply_markup=menu_keyboard_free)
    else:
        await message.answer(
            f"Бесплатные запросов осталось {free_req}. Оформите подписку для дальнейшего использования бота.",
            reply_markup=inline_markup_submit)


# ===================================================================================================================
#                                            ПОДПИСКА
# ===================================================================================================================

@dp.message_handler(lambda message: message.text == "💰 Подписка")
async def send_subscription_menu(message: types.Message):
    user_id = message.from_user.id
    # Проверяем есть ли пользователь в базе
    if get_user(user_id):
        if get_subscription(user_id) is None:
            await message.answer("Выберите тип подписки:", reply_markup=inline_markup_submit)
        else:
            subscription = get_subscription(user_id)
            await message.answer(f"У вас действует подписка {subscription}. Для инвормации используйте меню 📝 Токены")
    else:
        await message.answer("Для этого необходима регистрация в нашем боте.", reply_markup=inline_markup_reg)


@dp.message_handler(lambda message: message.text == "📝 Информация по подписке")
async def send_subscription_info(message: types.Message):
    await message.answer("Подписки:\nСтарт - 150 р. (лимит: 10000 токенов)"
                         "\nКомфорт - 500 р. (лимит: 50000 токенов)"
                         "\nПрофи - 1000 р. (лимит: 100000 токенов)", reply_markup=inline_markup_reg)


@dp.message_handler(lambda message: message.text == "📝 Остаток запросов")
async def send_subscription_info(message: types.Message):
    free_request = get_free_request(user_id=message.from_user.id)
    await message.answer(f"Количество бесплатных запросов осталось: {free_request}", reply_markup=inline_markup_reg)


# ===================================================================================================================
#                                            ПРОФИЛЬ
# ===================================================================================================================
@dp.message_handler(lambda message: message.text == "📊 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    # Проверяем есть ли пользователь в базе
    if get_user(user_id):
        # Получаем информацию о пользователе
        cursor.execute('SELECT user_id, registration_date FROM users WHERE user_id = ?', (user_id,))
        user_info = cursor.fetchone()
        user_id, registration_date = user_info

        # Функция для получения баланса пользователя
        balance = get_user_balance(user_id)

        # Функция для получения информации о подписке пользователя
        subscription_info = get_subscription_info(user_id)
        if get_subscription(user_id):
            subscription = get_subscription(user_id)
        else:
            subscription = "Нет"
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
        await message.answer("Для этого необходима регистрация в нашем боте.", reply_markup=inline_markup_reg)


# ===================================================================================================================
#                                            ТОКЕНЫ
# ===================================================================================================================
@dp.message_handler(lambda message: message.text == "📝 Токены")
async def show_tokens(message: types.Message):
    user_id = message.from_user.id
    # Проверяем есть ли пользователь в базе
    if get_user(user_id):
        cursor.execute('SELECT subscribe, tokens, tokens_used FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            subscribe_type, total_tokens, tokens_used = user_data
            remaining_tokens = total_tokens - tokens_used
            if total_tokens != 0:
                response_text = (
                    f'Общее количество токенов по подписке "{subscribe_type}": {total_tokens}\n'
                    f'\nОставшееся количество токенов: {remaining_tokens}'
                )
                await message.answer(response_text, reply_markup=menu_keyboard)
            else:
                await message.answer("У вас нет действующей подписки или вы не приобретали дополнительный пакет токенов.\n\
Для этого вам надо из меню выбрать интересующий вас вариант", reply_markup=inline_markup_submit)
    else:
        await message.answer("Для этого необходима регистрация в нашем боте.", reply_markup=inline_markup_reg)


# ===================================================================================================================
#                                            ЧАТ
# ===================================================================================================================
@dp.message_handler(lambda message: message.text == "👥 Создать чат")
async def create_chat(message: types.Message):
    user_id = message.from_user.id
    if get_user(user_id):
        # Создаем новый чат для пользователя
        cursor.execute('''
            UPDATE users
            SET chat_history = ?,
                response_history = ?
            WHERE user_id = ?
        ''', ('[]', '[]', user_id))  # Обнуляем историю чата
        conn.commit()

        await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)
    else:
        free_request = get_free_request(user_id)
        await message.answer(f"Новый чат создан! Теперь вы можете начать новый диалог.\n"
                             f"У вас {free_request} запросов", reply_markup=menu_keyboard_free)


# ===================================================================================================================
#
# ===================================================================================================================
@dp.message_handler(commands=['dalle'])
async def send_image(message: types.Message):
    api_key = get_unused_key()
    response = openai.Image.create(
        api_key=api_key,
        prompt=message.text,
        n=1,
        size="1024x1024",
    )
    await message.answer_photo(response["data"][0]["url"])


# ===================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "СТАРТ"
# ===================================================================================================================
@dp.callback_query_handler(text='st')
async def submit_start(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки",
                           description="qwe",
                           payload="month_sub", provider_token=YOOTOKEN, currency="RUB",
                           start_parameter="test_bot",
                           prices=[LabeledPrice(label="Руб", amount=15000)])
    Buf.name = "Старт"


# ===================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "КОМФОРТ"
# ===================================================================================================================
@dp.callback_query_handler(text='komf')
async def submit_komf(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки",
                           description="Подписка - Комфорт",
                           payload="month_sub", provider_token=YOOTOKEN, currency="RUB",
                           start_parameter="test_bot",
                           prices=[LabeledPrice(label="Руб", amount=50000)])
    Buf.name = "Комфорт"


# ===================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "ПРОФИ"
# ===================================================================================================================
@dp.callback_query_handler(text='pro')
async def submit_pro(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id,
                           title="Оформление подписки",
                           description="Подписка - Профи",
                           payload="month_sub",
                           provider_token=YOOTOKEN,
                           currency="RUB",
                           start_parameter="test_bot",
                           prices=[LabeledPrice(label="Руб", amount=100000)])
    Buf.name = "Профи"


# ===================================================================================================================
#                                            РЕГИСТРАЦИЯ
# ===================================================================================================================
@dp.callback_query_handler(text='reg')
async def process_registration(call: types.CallbackQuery):
    user_id = call.from_user.id
    username = call.from_user.username
    registration_date = call.message.date

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

    await call.message.answer(response_text, reply_markup=menu_keyboard)


# Декоратор - ответ сервису на наличие товара
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# ===================================================================================================================
#                                            ОПЛАТА ПОДПИСКИ
# ===================================================================================================================
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    subscribe_type = Buf.name
    sub_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tokens = 0

    if subscribe_type == 'Старт':
        tokens = 10000
    elif subscribe_type == 'Комфорт':
        tokens = 50000
    elif subscribe_type == 'Профи':
        tokens = 100000

    cursor.execute('''
            UPDATE users
            SET subscribe = ?, sub_date = ?, tokens = ?
            WHERE user_id = ?
        ''', (subscribe_type, sub_date, tokens, user_id))
    conn.commit()

    response_text = f'Вы выбрали подписку тариф {subscribe_type}. Вам доступно {tokens} токенов. Спасибо!'
    await message.answer(response_text, reply_markup=menu_keyboard)


# ===================================================================================================================
#                                            ЛЮБОЕ СООБЩЕНИЕ
# ===================================================================================================================
@dp.message_handler()
async def process_question(message: types.Message):
    user_id = message.from_user.id
    free_req = get_free_request(user_id)
    user_question = message.text
    user_history, response_history = ['', '']
    print(f"User question: {user_question}")
    if (get_user(user_id) and get_subscription(user_id)) or free_req != 0:
        # Если команда /dalle встречается в тексте сообщения, вызываем функцию send_image
        if "/dalle" in user_question:
            await send_image(message)
            return

        # Отправляем анимацию перед запросом к OpenAI GPT
        processing_message = await message.answer("🔄 Обработка запроса...")

        # Получаем текущую историю пользователя
        cursor.execute('SELECT chat_history, response_history FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
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
            json.dumps(user_history, ensure_ascii=False), json.dumps(response_history, ensure_ascii=False),
            user_id))
        conn.commit()

        # Имитация анимации перед запросом к OpenAI GPT завершена

        response = generate_response(user_history, user_id, message)
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
        await message.answer(response, reply_markup=menu_keyboard)
    else:
        await message.answer(f"Для дальнейшего использования бота вам нужно зарегистрироваться.",
                             reply_markup=inline_markup_reg)
