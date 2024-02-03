import json
import random
import openai
from aiogram import types
from app.moduls import generate_response, profile, counting_pay, Subscribe
from app.update_keys import get_unused_key
from data.config import bot, chat_id
from data.db_app import reg_user, new_chat, get_user_history, update_user_history, \
    add_response_to_history, calculate_remaining_tokens, set_state_ai, get_state_ai, get_flag_and_req, add_user
from data.metadata import Metadata
from nav.keyboard import inline_markup_reg, menu_keyboard, menu_profile, inline_submit_preview, inline_tp, menu_ai, \
    inline_submit_period

options = [
    "🤔 Осторожно, работает умная машина...",
    "⏳ Подождите, я тут кручусь и думаю...",
    "🌟 Работаю над вашим запросом, скоро все будет!",
    "🧠 Мозговой штурм в процессе, немного терпения!"
]


async def start_cmd(message: types.Message):
    first_name = message.from_user.first_name
    username = message.from_user.username
    user_id = message.from_user.id
    await add_user(user_id, username)
    await message.answer(
        f'Привет, {first_name}!\nДля пользования ботом, подпишитесь на наш новостной канал и нажмите "Готово". '
        f'Вы получите 15 бесплатных запросов для диалога с IZI и '
        f'5 запросов для генерации изображений.', reply_markup=inline_markup_reg)


# ======================================================================================================================
#                               Подписка
# ======================================================================================================================
async def submit(call: types.CallbackQuery):
    user_id = call.from_user.id
    flag, request, request_img = await get_flag_and_req(user_id)

    if flag == 2:
        await bot.edit_message_text(
            'Заглушка - флаг 3.',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_submit_preview
        )
    elif flag == 3:
        await call.answer(
            'Заглушка - флаг 4',
            reply_markup=menu_keyboard)
    elif flag == 4:
        await call.answer(
            'Заглушка - флаг 5',
            reply_markup=menu_keyboard)
    else:
        subscribe_text = await Subscribe()
        await bot.edit_message_text(subscribe_text,
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=inline_submit_preview)


async def Light(call: types.CallbackQuery):
    await bot.edit_message_text(
        'На какой период хотите оформить подписку Light?',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=inline_submit_period
    )
    Metadata.subscription = 'Подписка Light'


async def Middle(call: types.CallbackQuery):
    await bot.edit_message_text(
        'На какой период хотите оформить подписку Middle?',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=inline_submit_period
    )
    Metadata.subscription = 'Подписка Middle'


async def Full(call: types.CallbackQuery):
    await bot.edit_message_text(
        'На какой период хотите оформить подписку Full?',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=inline_submit_period
    )
    Metadata.subscription = 'Подписка Full'


async def month(call: types.CallbackQuery):
    description = 'ключевые моменты подписки'
    await counting_pay(1, description, call.from_user.id)


async def month_6(call: types.CallbackQuery):
    description = 'ключевые моменты подписки'
    await counting_pay(5, description, call.from_user.id)


async def year(call: types.CallbackQuery):
    description = 'ключевые моменты подписки'
    await counting_pay(10, description, call.from_user.id)


async def back_to_subscriptions(call: types.CallbackQuery):
    subscribe_text = await Subscribe()
    await bot.edit_message_text(subscribe_text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_submit_preview)


async def cancel_payment(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


# ======================================================================================================================
#                               Техподдержка
# ======================================================================================================================
async def tp(call: types.CallbackQuery):
    await bot.edit_message_text('Этот раздел еще в разработке...',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_tp)


# ======================================================================================================================
#                               Возврат в главное меню профиля
# ======================================================================================================================
async def back_to_profile(call: types.CallbackQuery):
    user_id = call.from_user.id
    profile_text = await profile(user_id)
    await bot.edit_message_text(profile_text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu_profile)


# ======================================================================================================================
#                               Проверка на членство в канале
# ======================================================================================================================
async def check_sub(call: types.CallbackQuery):
    user_id = call.from_user.id
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(member)
    if member.status != 'left':
        flag, request, request_img = await get_flag_and_req(user_id)
        if flag == 0 or flag is None:
            username = call.from_user.username
            flag = 1
            request = 15
            request_img = 5
            registration_date = call.message.date.strftime('%Y-%m-%d %H:%M:%S')
            await reg_user(user_id, username, registration_date, request, request_img, flag)
            await call.message.answer(
                f'Спасибо за подписку на наш канал! У вас 15 бесплатных запросов для диалога с IZI и '
                f'5 запросов для генерации изображений.',
                reply_markup=menu_keyboard)
        else:
            await call.message.answer(
                f'Спасибо за подписку на наш канал! У вас {request} бесплатных запросов для диалога с IZI и '
                f'{request_img} запросов для генерации изображений.',
                reply_markup=menu_keyboard)
    else:
        await call.answer('Для начала подпишись на наш новостной канал')


# ======================================================================================================================
#                               Выбор нейронки
# ======================================================================================================================
async def delle_2(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'delle2'
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Ок! Дальше я на ваши сообщения буду отвечать изображениями 👩‍🎨')


async def delle_3(call: types.CallbackQuery):
    await call.message.answer('Данный раздел находится в разработке, но скоро будет доступен...')


async def bot_dialog(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = ''
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Понял! Возвращаемся к обычному общению.')


# ======================================================================================================================
#                               Запрос Delle 2
# ======================================================================================================================
async def send_image(message):
    api_key = await get_unused_key()
    print(api_key)
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
    user_id = message.from_user.id
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(member)
    if member.status != 'left':
        text = message.text
        result = await get_flag_and_req(user_id)
        flag, request, request_img = result
        # ==================================================================================================================
        #                                             Профиль
        # ==================================================================================================================
        if text in ['📊 Профиль']:
            profile_text = await profile(user_id)
            await message.answer(profile_text, reply_markup=menu_profile)
        # ==================================================================================================================
        #                                             Нейросеть
        # ==================================================================================================================
        elif text in ['🧠 Нейросеть']:
            await message.answer('Теперь можете переключить нейросеть для ваших дальнейших запросов к боту',
                                 reply_markup=menu_ai)
        # ==================================================================================================================
        #                                             Создать чат
        # ==================================================================================================================
        elif text in ['👥 Создать чат']:
            await new_chat(user_id)
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)
        # ==================================================================================================================
        #                                             Любой запрос к боту
        # ==================================================================================================================
        else:
            state_ai = await get_state_ai(user_id)
            if state_ai == 'delle2' and request_img > 0:
                # Отправляем анимацию перед запросом к OpenAI GPT
                processing_message = await message.answer(random.choice(options))
                await send_image(message)
                # Удаляем сообщение с анимацией перед отправкой ответа
                await bot.delete_message(chat_id=processing_message.chat.id,
                                         message_id=processing_message.message_id)
            else:
                await message.answer('Дневной лимит для генерации изображений исчерпан. Жди следующего дня или можешь '
                                     'выбрать тариф и продолжить',
                                     reply_markup=inline_submit_preview)
            if flag > 0 and request > 0:
                user_question = message.text
                print(f"User question: {user_question}")
                # Отправляем анимацию перед запросом к OpenAI GPT
                processing_message = await message.answer(random.choice(options))

                # Получаем текущую историю пользователя
                chat_history, response_history = await get_user_history(user_id)

                chat_history = json.loads(chat_history) if chat_history else []
                response_history = json.loads(response_history) if response_history else []

                # Добавляем новое сообщение к истории
                chat_history.append({"role": "user", "content": user_question})

                # Обновляем историю в базе данных
                await update_user_history(user_id, chat_history, response_history)

                # Имитация анимации перед запросом к OpenAI GPT завершена

                response = await generate_response(user_id, chat_history, message)
                print(f"OpenAI response: {response}")

                # Удаляем сообщение с анимацией перед отправкой ответа
                await bot.delete_message(chat_id=processing_message.chat.id,
                                         message_id=processing_message.message_id)

                # Добавляем ответ к истории ответов
                response_history.append({"role": "assistant", "content": response})

                await add_response_to_history(user_id, response_history)

                await message.answer(response, reply_markup=menu_keyboard)

                await calculate_remaining_tokens(user_id)
            else:
                await message.answer('Дневной лимит для ответов IZI исчерпан. Жди следующего дня или можешь '
                                     'выбрать тариф и продолжить',
                                     reply_markup=inline_submit_preview)
    else:
        await message.answer("Для использования бота подпишите на наш канал",
                             reply_markup=inline_markup_reg)
