import ast
import json
import os
import random
from enum import member
from aiogram.methods.send_media_group import SendMediaGroup
import openai
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from aiogram.utils import media_group
from aiogram.utils.payload import decode_payload
from app.modul_Kandinsky3_0 import send_image_kandinsky
from app.modul_Kandinsky2_2 import kandinsky2_2
from app.moduls import generate_response, profile, counting_pay, Subscribe, calc_sum, ref_menu
from app.update_keys import get_unused_key
from data.config import bot, chat_id
from data.db_app import (reg_user, new_chat, get_user_history, update_user_history,
                         add_response_to_history, set_state_ai, get_state_ai, add_user, update_requests, get_flag,
                         get_req, save_banking_details, get_balans)
from data.metadata import Metadata
from nav.keyboard import (inline_markup_reg, menu_keyboard, menu_profile, inline_submit_preview, inline_tp, menu_ai,
                          menu_profile_ref, inline_back_to_ref)
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import CommandObject

options = [
    "🤔 Осторожно, работает умная машина...",
    "⏳ Подождите, я тут кручусь и думаю...",
    "🌟 Работаю над вашим запросом, скоро все будет!",
    "🧠 Мозговой штурм в процессе, немного терпения!"
]


async def start_cmd(message: types.Message, command: CommandObject):
    first_name = message.from_user.first_name
    username = message.from_user.username
    user_id = message.from_user.id
    referrer = None

    args = command.args  # Получаем зашифрованный ID реферера
    if args:
        # Дешифруем ID реферера
        referrer = decode_payload(args)
        referrer = int(referrer)

        if int(referrer) != user_id:
            ref_username = await get_username_by_user_id(bot, referrer)
            # Обновляем данные пользователя
            await add_user(user_id, username, referrer, True)

            if ref_username:
                await message.answer(f'Ваш реферер: \nid: {referrer}'
                                     f'\n{ref_username}')
                await message.answer(
                    f'Привет, {first_name}! \n\nДля пользования ботом, подпишитесь на наш новостной канал и нажмите '
                    f'"Готово". Вы получите 30 бесплатных запросов диалогах с Izi и 10 '
                    f'запросов на генерацию изображений.\n\n Примеры ответов 👇🏻',
                    reply_markup=inline_markup_reg)
                # Отправляем изображение в сообщении
                image1 = InputMediaPhoto(type='photo', media=FSInputFile(f"res/Kandinsky2_2.jpg"),
                                         caption='Нейросеть Кандинский 2.2\nЗапрос: "red cat, 4k photo"')
                image2 = InputMediaPhoto(type='photo', media=FSInputFile(f"res/Kandinsky3_0.jpg"),
                                         caption='Нейросеть Кандинский 3.0\nЗапрос: "Изящество и красота '
                                                 'могут проявляться даже в самых суровых условиях первобытностиColor '
                                                 'Grading, Shot on 70mm, Daguerrotype, F/2.8, CRT"')
                media = [image1, image2]

                await bot.send_media_group(user_id, media)

                # Уведомляем реферера
                await bot.send_message(chat_id=referrer, text=f'Ваш реферал теперь с нами: \nid: {user_id}'
                                                              f'\n{username}')
            else:
                await message.answer('Не найдено информации о пользователе, который вас пригласил.')
        else:
            await message.answer('Вы перешли по своей же ссылке 😄')
    else:
        result = await get_flag(user_id)

        # Если в БД нет пользователя, добавляем
        if not result:
            await add_user(user_id, username, referrer, False)
        await message.answer(
            f'Привет, {first_name}!\nДля пользования ботом, подпишитесь на наш новостной канал и нажмите "Готово". '
            'Вы получите 30 бесплатных запросов диалогах с Izi и 10 запросов на генерацию изображений.'
            '\n\n Примеры ответов 👇🏻',
            reply_markup=inline_markup_reg)
        # Отправляем изображение в сообщении
        image1 = InputMediaPhoto(type='photo', media=FSInputFile(f"res/Kandinsky2_2.jpg"),
                                 caption='Нейросеть Кандинский 2.2\nЗапрос: "red cat, 4k photo"')
        image2 = InputMediaPhoto(type='photo', media=FSInputFile(f"res/Kandinsky3_0.jpg"),
                                 caption='Нейросеть Кандинский 3.0\nЗапрос: "Изящество и красота '
                                         'могут проявляться даже в самых суровых условиях первобытностиColor '
                                         'Grading, Shot on 70mm, Daguerrotype, F/2.8, CRT"')
        media = [image1, image2]

        await bot.send_media_group(user_id, media)


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
    flag = await get_flag(user_id)

    if flag > 1:
        await bot.edit_message_text(
            'У вас еще действует тариф, вся информация в вашем личном кабинете',
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
    Metadata.subscription = 'Light'
    await calc_sum(100)
    Metadata.sub_sum_db = 100
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
    Metadata.sub_sum_db = 250
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
    Metadata.subscription = 'Premium'
    Metadata.sub_sum = 45000
    await calc_sum(450)
    Metadata.sub_sum_db = 450
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
        flag = await get_flag(user_id)

        result = await get_req(user_id)
        if result:
            request, request_img = result
        if flag is None or flag == 0:
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
                f'Спасибо за подписку на наш новостной канал! Вам доступно на данный момент бесплатно {request} '
                f'запросов для диалога и {request_img} запросов для генерации изображений 🫶🏻',
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
                              '\nВыберите объект. Это может быть все, что угодно: человек, '
                              'животное, сказочный персонаж, город, пейзаж, здание, автомобиль и '
                              'любой другой физический объект. Укажите число объектов, но помните, '
                              'что чем их больше, тем менее детализированными они будут. Пробуйте '
                              'совмещать два объекта, например, «киберпанк-город» или «кот, похожий '
                              'на картину “Мона Лиза”». Это позволит вам получить яркий и необычный концепт.\n\n'
                              'Запрос должен быть как можно более детальным, в нем должны быть описаны конкретные '
                              'предметы, а не абстрактные понятия. Так, вместо слов «инопланетная жизнь» '
                              'задайте «пятизвездочный отель на далекой планете».\n\n'
                              'Не используйте слова, выражающие отрицание («не», «кроме», «без», «за исключением», '
                              '«никакой»), и деепричастные обороты. Нейросеть не поймет их, в результате '
                              'вам придется переформулировать запрос. Для работы с негативным промптом '
                              'используйте отдельную функцию «изменить негативный промпт» и напишите, '
                              'что не хотите видеть на изображении: например, «тусклые цвета», «текст».\n\n'
                              'Добавляйте детали: как выглядит объект, что делает, в каком он настроении, где '
                              'расположен на картинке, что еще находится в кадре, какая цветовая палитра и освещение, '
                              'какое разрешение используется. Например, «футуристическая девушка из будущего, '
                              'фантастические космические цветы, крупный план, кружевное платье и доспехи, 4K, '
                              'кинематографический свет, гиперреалистичность, сверхдетализация, реализм, '
                              'фотореалистичный стиль».\n\n'
                              'Экспериментируйте со стилями. В Kandinsky 2.2 их множество — от фотографии, '
                              'аниме, поп-арта и мультфильма до хохломы, цифровой живописи и т. д. ')


# ======================================================================================================================
#                               Выбор нейронки
# ======================================================================================================================
async def kandinsky3_0(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'kandinsky3_0'
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
    state_ai = 'gpt'
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
#                                             Реф ссылка
# ======================================================================================================================
async def get_ref(call: types.CallbackQuery):
    link = await create_start_link(bot, str(call.from_user.id), encode=True)
    await bot.edit_message_text(f"Ваша реферальная ссылка:\n{link}\n\n"
                                f"Поделитесь ей вашим друзьям и получите бонус 💲. "
                                f"🎁 Вы будете получать 10% с первой оплаты "
                                f"тарифа каждого приглашенного вами пользователя.\n"
                                f"💰 Баланс можно контролировать в личном кабинете.\n\n"
                                f"Как можно использовать накопленный бонус:\n"
                                f"• оплатить свой тариф или компенсировать часть его стоимости\n"
                                f"• вывести на карту (в личного кабинете "
                                f"добавьте ваши реквизиты для перевода 💳)",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_back_to_ref)


# ======================================================================================================================
#                                             Меню партнерки
# ======================================================================================================================
async def ref_program(call: types.CallbackQuery):
    ref_text = await ref_menu()
    await bot.edit_message_text(ref_text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu_profile_ref)


async def requisites(call: types.CallbackQuery):
    await set_state_ai(call.from_user.id, 'Ожидание реквизитов для вывода')
    await bot.edit_message_text('Напишите мне ваши реквизиты, куда вам было бы удобно вывести ваш бонус.\n'
                                'Это может быть, номер карты, номер телефона (для СБП).'
                                'Данную информацию можно указать с пояснением (пример: +79991112244 '
                                'сбербанк Иванов И.И.)',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_back_to_ref)


async def get_the_money(call: types.CallbackQuery):
    await set_state_ai(call.from_user.id, 'Ожидание суммы для вывода')
    balans = await get_balans(call.from_user.id)
    await bot.edit_message_text(f"Ваш баланс: {balans}\n\nНапишите боту сумму для вывода",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_back_to_ref)


# ======================================================================================================================
#                                             Любой запрос
# ======================================================================================================================
async def echo(message: types.Message):
    user_id = message.from_user.id
    member_check = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(f"Проверка на подписку в новостном канале\n"
          f"Статус: {member_check.status}\n"
          f"ID: {member_check.user.id}\n"
          f"username: {member_check.user.username}\n"
          f"first_name: {member_check.user.first_name}\n"
          f"is_bot: {member_check.user.is_bot}\n")

    if member_check.status != 'left':
        text = message.text
        result = await get_req(user_id)
        if result:
            request, request_img = result
        # ==================================================================================================================
        #                                             Профиль
        # ==================================================================================================================
        if text in ['📊 Личный кабинет']:
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
        elif text in ['Начать общение с IZI']:
            await new_chat(user_id)
            await set_state_ai(user_id, 'gpt')
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)
        # ==================================================================================================================
        #                                             Любой запрос к боту
        # ==================================================================================================================
        else:
            state_ai = await get_state_ai(user_id)

            if state_ai == 'Ожидание суммы для вывода':
                text_request = await profile(user_id, 1)
                balans = await get_balans(user_id)
                if balans == 0:
                    await message.answer(f"К сожалению вам пока ничего выводить, ваш баланс: {balans}",
                                         reply_markup=inline_back_to_ref)
                if balans >= int(text):
                    await bot.send_message(6280608864, f'Заявка на вывод бонуса:\n\n{text_request}\n\n'
                                                       f'На сумму: {text}')
                    await message.answer(f"Заявка на вывод бонуса отправлена администратору, "
                                         f"средства поступят в течении дня.",
                                         reply_markup=inline_back_to_ref)
                else:
                    await message.answer(f"Вы указали некорректную сумму, ваш баланс: {balans}",
                                         reply_markup=inline_back_to_ref)
                await set_state_ai(user_id, 'gpt')

            elif state_ai == 'Ожидание реквизитов для вывода':
                await save_banking_details(user_id, text)
                await message.answer(f"Данные для перевода бонуса на ваш счет сохранены: {text}",
                                     reply_markup=inline_back_to_ref)
                await set_state_ai(user_id, 'gpt')

            elif state_ai == 'gpt':
                if request != 0:
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

                    await message.answer(str(response), reply_markup=menu_keyboard)
                else:
                    await message.answer('Дневной лимит для ответов Izi исчерпан. Выберите тариф и продолжите 🛒',
                                         reply_markup=inline_submit_preview)
            elif request_img != 0:
                if state_ai == 'delle2':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(options))

                    await send_image(message)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)

                elif state_ai == 'kandinsky3_0':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(options))

                    styles = ["KANDINSKY", "UHD", "ANIME", "DEFAULT"]
                    for style in styles:
                        await send_image_kandinsky(message, message.text, style)
                        FSInputFile(f"image_Kandinsky3_0/{message.from_user.id}+{style}.jpg")

                    image1 = InputMediaPhoto(type='photo', media=FSInputFile(
                        f"image_Kandinsky3_0/{message.from_user.id}+KANDINSKY.jpg"), caption='Стиль: KANDINSKY')
                    image2 = InputMediaPhoto(type='photo', media=FSInputFile(
                        f"image_Kandinsky3_0/{message.from_user.id}+UHD.jpg"), caption='Стиль: UHD')
                    image3 = InputMediaPhoto(type='photo', media=FSInputFile(
                        f"image_Kandinsky3_0/{message.from_user.id}+ANIME.jpg"), caption='Стиль: ANIME')
                    image4 = InputMediaPhoto(type='photo', media=FSInputFile(
                        f"image_Kandinsky3_0/{message.from_user.id}+DEFAULT.jpg"), caption='Стиль: DEFAULT')

                    media = [image1, image2, image3, image4]

                    await bot.send_media_group(user_id, media)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)

                elif state_ai == 'kandinsky2_2':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(options))

                    await kandinsky2_2(message, message.text)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)
            elif request_img == 0:
                await message.answer(
                    'Суточный лимит для генерации изображений исчерпан. Выберите тариф и продолжите 🛒',
                    reply_markup=inline_submit_preview)
    else:
        await message.answer("Для использования бота подпишите на наш канал ✔️",
                             reply_markup=inline_markup_reg)
