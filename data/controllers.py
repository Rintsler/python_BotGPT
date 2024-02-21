import json
import random
import openai
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.payload import decode_payload

from app.modul_Kandinsky import send_image_kandinsky
from app.modul_Kandinsky2_2 import kandinsky2_2
from app.moduls import generate_response, profile, counting_pay, Subscribe, calc_sum
from app.update_keys import get_unused_key
from data.config import bot, chat_id
from data.db_app import reg_user, new_chat, get_user_history, update_user_history, \
    add_response_to_history, set_state_ai, get_state_ai, get_flag_and_req, add_user, update_requests
from data.metadata import Metadata
from nav.keyboard import inline_markup_reg, menu_keyboard, menu_profile, inline_submit_preview, inline_tp, menu_ai
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import CommandObject

options = [
    "🤔 Осторожно, работает умная машина...",
    "⏳ Подождите, я тут кручусь и думаю...",
    "🌟 Работаю над вашим запросом, скоро все будет!",
    "🧠 Мозговой штурм в процессе, немного терпения!"
]


async def start_cmd(message: types.Message, command: CommandObject):
    payload = None
    first_name = message.from_user.first_name
    username = message.from_user.username
    user_id = message.from_user.id
    result = await get_flag_and_req(user_id)
    args = command.args
    try:
        payload = decode_payload(args)
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе в Start: {e}")
    if payload:
        ref_username = await get_username_by_user_id(bot, int(payload))
        await add_user(user_id, username, payload, True)
        await message.answer(f'Ваш реферер: \nid:{payload}'
                             f'\n{ref_username}')
    if not result:
        await add_user(user_id, username, payload, False)
    await message.answer(
        f'Привет, {first_name}!\nДля пользования ботом, подпишитесь на наш новостной канал и нажмите "Готово". '
        'Вы получите 30 бесплатных запросов диалогах с Izi и 10 запросов на генерацию изображений.',
        reply_markup=inline_markup_reg)


async def get_username_by_user_id(bot: Bot, user_id: int):
    try:
        user = await bot.get_chat_member(chat_id=user_id, user_id=user_id)
        return user.user.username if user.user.username else "Имя пользователя отсутствует"
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None


# ======================================================================================================================
#                               Подписка
# ======================================================================================================================
async def submit(call: types.CallbackQuery):
    user_id = call.from_user.id
    flag, request, request_img = await get_flag_and_req(user_id)

    if flag > 1:
        await bot.edit_message_text(
            'У вас еще действует тариф, вся информация в вашем профиле',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_submit_preview
        )
    else:
        subscribe_text = await Subscribe()
        await bot.edit_message_text(subscribe_text,
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=inline_submit_preview)


# ======================================================================================================================
#                               Выбор тарифа
# ======================================================================================================================
async def Light(call: types.CallbackQuery):
    Metadata.sub_sum = 10000
    await calc_sum(100)
    Metadata.subscription = 'Light'
    await bot.edit_message_text('📝 Диалог с Izi - 35 запросов в сутки\n'
                                '🖼️ Генерация изображений - 15 запросов в сутки\n'
                                'На какой период хотите подключить тариф - Базовый?',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text=f'Месяц - {Metadata.sub_sum1} р.',
                                                                 callback_data='month')
                                        ],
                                        [
                                            InlineKeyboardButton(text=f'6 месяцев - {Metadata.sub_sum2} р.',
                                                                 callback_data='month_6')
                                        ],
                                        [
                                            InlineKeyboardButton(text=f'Год - {Metadata.sub_sum3} р.',
                                                                 callback_data='year')
                                        ],
                                        [
                                            InlineKeyboardButton(text="← назад", callback_data='back_to_subscriptions')
                                        ]
                                    ],
                                    resize_keyboard=True
                                )
                                )


async def Middle(call: types.CallbackQuery):
    Metadata.sub_sum = 25000
    Metadata.subscription = 'Middle'
    await calc_sum(250)
    await bot.edit_message_text('📝 Диалог с Izi - без ограничений 😺\n'
                                '🖼️ Генерация изображений - 40 запросов в сутки\n'
                                'На какой период хотите подключить тариф - Расширенный?',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text=f'Месяц - {Metadata.sub_sum1} р.',
                                                                 callback_data='month')
                                        ],
                                        [
                                            InlineKeyboardButton(text=f'6 месяцев - {Metadata.sub_sum2} р.',
                                                                 callback_data='month_6')
                                        ],
                                        [
                                            InlineKeyboardButton(text=f'Год - {Metadata.sub_sum3} р.',
                                                                 callback_data='year')
                                        ],
                                        [
                                            InlineKeyboardButton(text="← назад", callback_data='back_to_subscriptions')
                                        ]
                                    ],
                                    resize_keyboard=True
                                )
                                )


async def Full(call: types.CallbackQuery):
    Metadata.sub_sum = 45000
    await calc_sum(450)
    Metadata.subscription = 'Premium'
    await bot.edit_message_text('♾️ Полный безлимит на запросы к Izi 🤩\n'
                                'На какой период хотите подключить тариф - Премиум?',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text=f'Месяц - {Metadata.sub_sum1} р.',
                                                                 callback_data='month')
                                        ],
                                        [
                                            InlineKeyboardButton(text=f'6 месяцев - {Metadata.sub_sum2} р.',
                                                                 callback_data='month_6')
                                        ],
                                        [
                                            InlineKeyboardButton(text=f'Год - {Metadata.sub_sum3} р.',
                                                                 callback_data='year')
                                        ],
                                        [
                                            InlineKeyboardButton(text="← назад", callback_data='back_to_subscriptions')
                                        ]
                                    ],
                                    resize_keyboard=True
                                )
                                )


# ======================================================================================================================
#                               Возврат к списку тарифов
# ======================================================================================================================
async def back_to_subscriptions(call: types.CallbackQuery):
    subscribe_text = await Subscribe()
    await bot.edit_message_text(subscribe_text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_submit_preview)


# ======================================================================================================================
#                               Выбор периода
# ======================================================================================================================
async def month(call: types.CallbackQuery):
    await counting_pay(1, call.from_user.id)
    Metadata.sub_period = 1


async def month_6(call: types.CallbackQuery):
    await counting_pay(5, call.from_user.id)
    Metadata.sub_period = 6


async def year(call: types.CallbackQuery):
    await counting_pay(10, call.from_user.id)
    Metadata.sub_period = 12


# ======================================================================================================================
#                               Отмена оплаты
# ======================================================================================================================
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
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print('Проверка на членство в канале: ', member)
    if member.status != 'left':
        flag, request, request_img = await get_flag_and_req(user_id)
        if flag == 0 or flag is None:
            flag = 1
            request = 30
            request_img = 10
            registration_date = call.message.date.strftime('%d.%m.%Y')
            await reg_user(user_id, registration_date, request, request_img, flag)
            await call.message.answer(
                'Спасибо за подписку на наш канал! У вас 30 бесплатных запросов диалогах с Izi и '
                '10 запросов на генерацию изображений 🫶🏻'
                'По исчерпании этого пакета, ежедневного бесплатно предоставляются 10 запросов для диалогов и '
                '5 запросов на генерацию изображений.',
                reply_markup=menu_keyboard)
        elif flag == 1:
            await call.message.answer(
                f'Спасибо за подписку на наш канал! Вам доступно на данный момент бесплатно {request} запросов для '
                f'диалога и {request_img} запросов для генерации изображений 🫶🏻',
                reply_markup=menu_keyboard)
        else:
            await call.message.answer(
                f'Спасибо что вы с нами! У вас действует подписка, вся информация есть в вашем профиле 😉',
                reply_markup=menu_keyboard)
    else:
        await call.message.answer('Для начала подпишись на наш новостной канал', reply_markup=inline_markup_reg)


# ======================================================================================================================
#                               Выбор нейронки
# ======================================================================================================================
async def for_kandinsky2_2(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'kandinsky2_2'
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Ок! Дальше я на ваши сообщения буду отвечать изображениями 👩‍🎨\n\n'
                              'Формула запроса для красивой картинки\n'
                              '\n- Описываем, что будет на изображении: '
                              'девушка, ребенок, кот, жираф, машина, яблоко, башня и т.д.'
                              '\n- Конкретизируем и добавляем детали запросу: какая одежда, '
                              'куда смотрит, поза, цвет и т.д.'
                              '\n- Далее даем информацию, где наш объект, какой у него фон: '
                              'море, город, горы, кабинет, без фона'
                              '\n- Определяем стиль: фотография, поп-арт, техно-мистика, барокко и т.д. '
                              '\n- Если стиля нет в списке доступных, то можно дописать его в запросе.\n\n'
                              'Чтобы получилось изображение близкое к фотографии, то допиши: 4K, '
                              'кинематографический свет, гиперреалистичность, сверхдетализация, '
                              'реализм, фотореалистичный стиль')


# ======================================================================================================================
#                               Выбор нейронки
# ======================================================================================================================
async def kandinsky(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'kandinsky'
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Ок! Дальше я на ваши сообщения буду отвечать изображениями 👩‍🎨\n\n'
                              'Формула запроса для красивой картинки\n'
                              '\n- Описываем, что будет на изображении: '
                              'девушка, ребенок, кот, жираф, машина, яблоко, башня и т.д.'
                              '\n- Конкретизируем и добавляем детали запросу: какая одежда, '
                              'куда смотрит, поза, цвет и т.д.'
                              '\n- Далее даем информацию, где наш объект, какой у него фон: '
                              'море, город, горы, кабинет, без фона'
                              '\n- Определяем стиль: фотография, поп-арт, техно-мистика, барокко и т.д. '
                              '\n- Если стиля нет в списке доступных, то можно дописать его в запросе.\n\n'
                              'Чтобы получилось изображение близкое к фотографии, то допиши: 4K, '
                              'кинематографический свет, гиперреалистичность, сверхдетализация, '
                              'реализм, фотореалистичный стиль')


async def delle_2(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'delle2'
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Ок! Дальше я на ваши сообщения буду отвечать изображениями 👩‍🎨\n\n'
                              'Для этой нейросети, запрос рекомендуется писать на английском, '
                              'но русский язык тоже допустим. '
                              '\n\nЧтобы получить качественный результат, используйте запросы, '
                              'которые будут чётко описывать желаемый кадр, но без излишних деталей. '
                              'В строке ввода стоит вписать тип изображения. Это может быть портрет, '
                              'картинка акварелью, карандашный набросок и тому подобное.\n\n'
                              'Также укажите вариант освещения в кадре и стиль. Допустим, реалистичное отображение, '
                              'как в комиксе или конкретную манеру известного художника. Дополнить это желательно '
                              'примерным уровнем яркости.\n\n'
                              'В конце строки можно дописать контекст происходящего. Например, что кадр содержит '
                              'не только луноход, но и момент, как тот движется на фоне Земли. Или сцену, на которой '
                              'плюшевые зайцы сражаются с инопланетянами.')


async def delle_3(call: types.CallbackQuery):
    await call.message.answer('Данный раздел находится в разработке, но скоро будет доступен ⏳')


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
#                                             Рефералка
# ======================================================================================================================
async def get_ref(message: types.Message, ):
    link = await create_start_link(bot, str(message.from_user.id), encode=True)
    await message.answer(f"Ваша реферальная ссылка:\n{link}")


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
        elif text in ['🗣 Пригласить друга']:
            await get_ref(message)
        # ==================================================================================================================
        #                                             Любой запрос к боту
        # ==================================================================================================================
        else:
            state_ai = await get_state_ai(user_id)
            if state_ai == 'delle2':
                if request_img != 0:
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(options))

                    await send_image(message)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)
                else:
                    await message.answer(
                        'Суточный лимит для генерации изображений исчерпан.',
                        reply_markup=inline_submit_preview)
            elif state_ai == 'kandinsky':
                if request_img != 0:
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(options))

                    await send_image_kandinsky(message, message.text)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)
            elif state_ai == 'kandinsky2_2':
                if request_img != 0:
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(options))

                    await kandinsky2_2(message, message.text)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)
                else:
                    await message.answer(
                        'Суточный лимит для генерации изображений исчерпан.',
                        reply_markup=inline_submit_preview)
            elif flag > 0 and request != 0:
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

                response = await generate_response(user_id, chat_history, message, request, request_img)
                print(f"OpenAI response: {response}")

                # Удаляем сообщение с анимацией перед отправкой ответа
                await bot.delete_message(chat_id=processing_message.chat.id,
                                         message_id=processing_message.message_id)

                # Добавляем ответ к истории ответов
                response_history.append({"role": "assistant", "content": response})

                await add_response_to_history(user_id, response_history)

                await message.answer(response, reply_markup=menu_keyboard)
            else:
                await message.answer('Дневной лимит для ответов Izi исчерпан. Выберите тариф и продолжите 🛒',
                                     reply_markup=inline_submit_preview)
    else:
        await message.answer("Для использования бота подпишите на наш канал ✔️",
                             reply_markup=inline_markup_reg)
