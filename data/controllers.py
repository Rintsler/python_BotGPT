import json

import aiosqlite
import openai
from aiogram import types
from data.bufer import B
from nav.keyboard import menu_keyboard_free, inline_markup_submit, inline_markup_reg, menu_keyboard
from app.moduls import get_subscription_info, generate_response
from app.update_keys import get_unused_key
from data.config import bot
from data.db_app import add_user, reg_user, get_flag, new_chat, get_user_history, update_user_history, \
    add_response_to_history, get_user, calculate_remaining_tokens, get_subscribe

user = B()


async def start_cmd(message: types.Message):
    user.user_id = message.from_user.id
    user_date = await get_user(user.user_id)
    if user_date is None:
        user.username = message.from_user.username
    text = f"Привет, {user.username}!\nЯ ваш телеграм-бот. " \
           f"Отправьте мне ваш вопрос, и я постараюсь ответить."
    if user.flag == 0 or user.flag is None:
        user.tokens = 10000
        user.flag = 1
        await add_user(user.user_id, user.username, user.tokens, user.flag)
        await message.answer(text, reply_markup=menu_keyboard_free)
        await message.answer(
            "Вам доступно 10000 бесплатных токенов, которые обновляются каждый понедельник.\n"
            "Для расширения функционала вам надо зарегистрироваться.",
            reply_markup=inline_markup_reg)
    elif user.flag == 1:
        if user.tokens == 0 or user.tokens is None:
            await message.answer(text, reply_markup=menu_keyboard_free)
            await message.answer(
                f"ВНИМАНИЕ: Бесплатные токены закончились.",
                reply_markup=inline_markup_reg)
        else:
            remaining_tokens = await calculate_remaining_tokens(message.from_user.id)
            await message.answer(text, reply_markup=menu_keyboard_free)
            await message.answer(f"Бесплатных токенов осталось {remaining_tokens}.",
                                 reply_markup=inline_markup_reg)
    elif user.flag == 2:
        await message.answer(text, reply_markup=menu_keyboard)
        await message.answer(
            'ВНИМАНИЕ: Бесплатные токены закончились. Оформите подписку для дальнейшего использования бота.',
            reply_markup=inline_markup_submit)


# ======================================================================================================================
#                                            РЕГИСТРАЦИЯ
# ======================================================================================================================
async def registration(call: types.CallbackQuery):
    if user.flag == 2:
        await call.message.answer("Вы уже зарегистрированы.", reply_markup=menu_keyboard)
    else:
        user.registration_date = call.message.date.strftime('%Y-%m-%d %H:%M:%S')
        user.flag = 2
        await reg_user(user.registration_date, user.flag, user.user_id)
        await call.message.answer("Регистрация успешна!", reply_markup=menu_keyboard)
        await call.message.answer("Можете оформить подписку.", reply_markup=inline_markup_submit)


async def send_image(message):
    api_key = get_unused_key()
    response = openai.Image.create(
        api_key=api_key,
        prompt=message.text,
        n=1,
        size="1024x1024",
    )
    await message.answer_photo(response["data"][0]["url"])


# ======================================================================================================================
#                                             Любой запрос
# ======================================================================================================================
async def echo(message: types.Message):
    user.user_id = message.from_user.id
    text = message.text
    user.flag = await get_flag(user.user_id)
    # ==================================================================================================================
    #                                             ПОДПИСКА
    # ==================================================================================================================
    if text in ['💰 Подписка']:
        # Проверяем есть ли пользователь в базе
        user.subscribe = await get_subscribe(user.user_id)
        if user.subscribe is not None:
            await message.answer(
                f"У вас действует подписка {user.subscribe}. Для информации используйте меню 📝 Токены")
        else:
            await message.answer("Выберите тип подписки:", reply_markup=inline_markup_submit)
    # ==================================================================================================================
    #                                             ПОДПИСКА
    # ==================================================================================================================
    elif text in ['⚙️ HELP']:
        if user.flag == 2:
            await message.answer(f"Раздел HELP {user.flag}", reply_markup=menu_keyboard)
        else:
            await message.answer(f"Раздел HELP {user.flag}", reply_markup=menu_keyboard_free)
    # ==================================================================================================================
    #                                             Информация по подписке
    # ==================================================================================================================
    elif text in ['📝 Тарифы']:
        await message.answer("Подписки:\nСтарт: 120р - 80тыс токенов"
                             "\nКомфорт: 250р - 150тыс токенов"
                             "\nПрофи: 500-600р - 300тыс токенов", reply_markup=inline_markup_reg)
    # ==================================================================================================================
    #                                             Профиль
    # ==================================================================================================================
    elif text in ['📊 Профиль']:
        await get_user(user.user_id)
        subscription_info = await get_subscription_info(user.user_id, user.sub_date)
        if user.registration_date is None:
            user.registration_date = ' '
        if user.balance is None:
            user.balance = ' '
        if user.subscribe is None:
            user.subscribe = ' '

        profile_text = (
            f"\t📊 Ваш профиль:\n"
            f"👤 Ваш айди: {user.user_id}\n"
            f"💰 Баланс: {user.balance} ₽\n"
            f"✅ Подписка: {user.subscribe}\n"
            f"📕 Остаток токенов по подписке: {subscription_info['remaining_tokens']}\n"
            f"⏳ Дата регистрации: {user.registration_date}\n"
            f"🗓 Осталось дней подписки: {subscription_info['remaining_days']}\n"
        )
        if user.remaining_tokens > 0:
            text_options = f"📕 Остаток бесплатных токенов: {user.remaining_tokens}\n"
            await message.answer(profile_text + text_options, reply_markup=menu_keyboard)
        else:
            await message.answer(profile_text, reply_markup=menu_keyboard)
    # ==================================================================================================================
    #                                             Токены
    # ==================================================================================================================
    elif text in ['📝 Токены']:
        if user.flag == 2 and user.subscribe is not None:
            response_text = (
                f'Общее количество токенов по подписке "{user.subscribe}": {user.tokens}\n'
                f'\nОставшееся количество токенов: {user.remaining_tokens}\n'
            )
            await message.answer(response_text + "Для перехода на другую подписку, выберите вариант ниже:",
                                 reply_markup=inline_markup_submit)
        elif user.flag == 1 and user.tokens != 0:
            response_text = (
                f'Общее количество бесплатных токенов: 10000\n'
                f'\nОставшееся количество токенов: {user.remaining_tokens}'
            )
            await message.answer(response_text, reply_markup=menu_keyboard)
            await message.answer("Бесплатные токены возвращаются каждый понедельник\n"
                                 "Так же вы можете оформить подписку с оптимальным вариантом для вас!",
                                 reply_markup=inline_markup_submit)
    # ==================================================================================================================
    #                                             Создать чат
    # ==================================================================================================================
    elif text in ['👥 Создать чат']:
        await new_chat(user.user_id)
        if user.flag == 2:
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)
        else:
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.",
                                 reply_markup=menu_keyboard_free)
    # ==================================================================================================================
    #                                             Любой запрос к боту
    # ==================================================================================================================
    else:
        user_question = message.text
        print(f"User question: {user_question}")
        # Отправляем анимацию перед запросом к OpenAI GPT
        processing_message = await message.answer("🔄 Обработка запроса...")

        # Получаем текущую историю пользователя
        chat_history, response_history = await get_user_history(user.user_id)

        chat_history = json.loads(chat_history) if chat_history else []
        response_history = json.loads(response_history) if response_history else []

        # Добавляем новое сообщение к истории
        chat_history.append({"role": "user", "content": user_question})

        # Обновляем историю в базе данных
        await update_user_history(user.user_id, chat_history, response_history)

        # Имитация анимации перед запросом к OpenAI GPT завершена

        response = await generate_response(user.user_id, chat_history, message)
        print(f"OpenAI response: {response}")

        # Удаляем сообщение с анимацией перед отправкой ответа
        await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

        # Имитация анимации после получения ответа от OpenAI GPT
        await message.answer("✅ Готово!")

        # Добавляем ответ к истории ответов
        response_history.append({"role": "assistant", "content": response})

        await add_response_to_history(user.user_id, response_history)

        if user.flag == 2:
            await message.answer(response, reply_markup=menu_keyboard)
        else:
            await message.answer(response, reply_markup=menu_keyboard_free)
