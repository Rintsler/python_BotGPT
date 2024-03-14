import json
import random
import openai
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.payload import decode_payload
from app.modul_Kandinsky2_2 import kandinsky2_2
from app.moduls import (generate_response, profile, counting_pay, Subscribe, calc_sum, ref_menu, media_group_img,
                        media_group_img_start)
from app.update_keys import get_unused_key
from data.config import bot, chat_id
from data.db_app import (reg_user, new_chat, get_user_history, update_user_history,
                         add_response_to_history, set_state_ai, get_state_ai, add_user, update_requests, get_flag,
                         get_req, get_balans, get_user)
from data.metadata import Metadata
from nav.keyboard import (inline_markup_reg, menu_keyboard, menu_profile, inline_submit_preview, inline_tp, menu_ai,
                          menu_profile_ref, inline_back_to_ref)
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import CommandObject
from aiogram.fsm.state import StatesGroup, State


class StateBot(StatesGroup):
    banking_details_input = State()
    bonus_output = State()


async def start_cmd(message: types.Message, command: CommandObject, state: FSMContext):
    await state.set_state(StateBot.s)
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

            if ref_username:
                check = await get_user(user_id)
                if not check:
                    # Обновляем данные пользователя
                    await add_user(user_id, username, referrer, True)
                    await message.answer('<b>Вы перешли в бота по ссылке друга. '
                                         'Он получит бонус от вашей первой оплаты тарифа. Приводите '
                                         'друзей по вашей ссылке (доступна в меню партнерская программа) '
                                         'и зарабатывайте!</b> 🤑',
                                         reply_markup=inline_markup_reg)

                    # Отправляем изображение в сообщении
                    media = await media_group_img_start()
                    await bot.send_media_group(user_id, media)

                    # Уведомляем реферера
                    await bot.send_message(chat_id=referrer, text=f'<b>Ваш реферал теперь с нами: \nid: {user_id}'
                                                                  f'\n{username}\n\n</b>'
                                                                  f'С первой оплаты его тарифа на ваш '
                                                                  f'баланс будет начислено 10% от его суммы оплаты!')
                else:
                    await message.answer('<b>🧐 Вы уже регистрировались, условия по реферальной ссылке '
                                         'работают только для новых пользователей</b>')
                    await message.answer_sticker(
                        'CAACAgIAAxkBAAEECUNl8BLj6i4vqtzflyxNDFMaxHsZUQACNxEAAl5L4Ete45bSAcoO1jQE')
            else:
                await message.answer('<b>🧐 Не найдено информации о пользователе, который вас пригласил. '
                                     'К сожалению ссылка недействительна 4️⃣0️⃣4️⃣</b>')
                await message.answer_sticker('CAACAgIAAxkBAAEECUNl8BLj6i4vqtzflyxNDFMaxHsZUQACNxEAAl5L4Ete45bSAcoO1jQE')
        else:
            await message.answer('Вы перешли по своей же ссылке 😄')
            await message.answer_sticker('CAACAgIAAxkBAAEECUNl8BLj6i4vqtzflyxNDFMaxHsZUQACNxEAAl5L4Ete45bSAcoO1jQE')

    check = await get_user(user_id)
    if not check:
        # Если в БД нет пользователя, добавляем
        await add_user(user_id, username, referrer, False)
        await message.answer(
            f'<b>Привет, {first_name}!</b>'
            f'\n\nДля пользования ботом, <b><i>подпишитесь</i></b> на наш новостной канал и нажмите \n'
            f'<b>[ ✔️ Готово ]</b>.\nВы получите <b><u>30 бесплатных</u></b> запросов диалогах с Izi и '
            f'<b><u>10 запросов</u></b> на генерацию изображений.',
            reply_markup=inline_markup_reg)

        # Отправляем изображение в сообщении
        media = await media_group_img_start()
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
    subscribe_text = await Subscribe()
    if flag > 1:
        await bot.edit_message_text(
            f'❗️❗️❗️ <b>Внимание</b>, у вас еще действует тариф.\n\n',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_submit_preview
        )
    else:
        await bot.edit_message_text(subscribe_text,
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=inline_submit_preview)


# =====================================================================================================================
# ПРОВЕРКА НА ЧЛЕНСТВО В КАНАЛЕ
# =====================================================================================================================
async def check_sub(call: types.CallbackQuery):
    user_id = call.from_user.id
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print('Проверка на подписку в новостном канале: ', member)
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
                'Спасибо за подписку на наш канал! У вас <b><u>30 бесплатных</u></b> запросов диалогах с Izi и '
                '<b><u>10 запросов</u></b> на генерацию изображений 🫶🏻'
                'По исчерпании этого пакета, ежедневного бесплатно предоставляются <b><u>10 запросов</u></b> '
                'для диалогов и <b><u>5 запросов</u></b> на генерацию изображений.',
                reply_markup=menu_keyboard)
        elif flag == 1:
            await call.message.answer(
                f'Спасибо за подписку на наш новостной канал! Вам доступно бесплатно <b><u>{request}</u></b> '
                f'запросов для диалога и <b><u>{request_img}</u></b> запросов для генерации изображений 🫶🏻',
                reply_markup=menu_keyboard)
        else:
            await call.message.answer(
                f'Спасибо что вы с нами!'
                f'\nУ вас действует подписка, вся информация '
                f'доступна по кнопке\n<b>[ 👤 Ваш профиль ]</b>" 😉',
                reply_markup=menu_keyboard)
    else:
        await call.message.answer('Для начала <b><u><i>подпишись</i></u></b> на наш новостной канал 😊',
                                  reply_markup=inline_markup_reg)


# ======================================================================================================================
#                               Выбор тарифа
# ======================================================================================================================
async def Light(call: types.CallbackQuery):
    Metadata.subscription = 'Light'
    Metadata.calc_sum_flag = True
    await calc_sum(100)
    Metadata.sub_sum_db = 100
    await bot.edit_message_text('📝 Диалог с Izi - <u>35 запросов в сутки</u>\n'
                                '🖼️ Генерация изображений - <u>15 запросов в сутки</u>\n\n'
                                '<b>На какой период хотите подключить тариф Базовый?</b>',
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
    Metadata.subscription = 'Middle'
    Metadata.calc_sum_flag = True
    await calc_sum(250)
    Metadata.sub_sum_db = 250
    await bot.edit_message_text('📝 Диалог с Izi - <u>без ограничений</u> 😺\n'
                                '🖼️ Генерация изображений - <u>40 запросов в сутки</u>\n\n'
                                '<b>На какой период хотите подключить тариф - Расширенный?</b>',
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
    Metadata.calc_sum_flag = True
    await calc_sum(450)
    Metadata.sub_sum_db = 450
    await bot.edit_message_text('♾️ <u>Полный безлимит</u> на запросы к Izi 🤩\n\n'
                                '<b>На какой период хотите подключить тариф - Премиум?</b>',
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
    Metadata.calc_sum_flag = True
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
    await bot.edit_message_text('По всем вопросам пишите нашему рядовому сотруднику, он обработает ваш запрос:'
                                ' https://t.me/Rintzler',
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
#                               Выбор нейронки
# ======================================================================================================================
async def for_kandinsky2_2(call: types.CallbackQuery):
    await call.answer('Данный раздел находится в разработке, но скоро будет доступен ⏳', show_alert=True)


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


async def dalle_2(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'dalle2'
    await set_state_ai(user_id, state_ai)
    await call.message.answer(f'<b>Ок! Дальше я на ваши сообщения буду отвечать изображениями</b> 👩‍🎨\n\n'
                              f'Для этой нейросети, запрос рекомендуется писать на английском, '
                              f'но русский язык тоже допустим. '
                              f'\n\nЧтобы получить качественный результат, используйте запросы, '
                              f'которые будут чётко описывать желаемый кадр, но без излишних деталей. '
                              f'В строке ввода стоит вписать <b>тип изображения</b>. Это может быть <b>портрет, '
                              f'картинка акварелью, карандашный набросок и тому подобное</b>.\n\n'
                              f'Также укажите вариант <b>освещения в кадре и стиль</b>. Допустим, реалистичное '
                              f'отображение, как в комиксе или конкретную манеру известного художника. '
                              f'Дополнить это желательно примерным уровнем яркости.\n\n'
                              f'В конце строки можно дописать <b>контекст происходящего</b>. Например, '
                              f'что кадр содержит не только луноход, но и момент, как тот движется '
                              f'на фоне Земли. Или сцену, на которой '
                              f'плюшевые зайцы сражаются с инопланетянами.')


async def dalle_3(call: types.CallbackQuery):
    await call.answer('Данный раздел находится в разработке, но скоро будет доступен ⏳', show_alert=True)


async def bot_dialog(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'gpt'
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Поняла! Возвращаемся к обычному общению.')


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
    await message.answer_photo(response["data"][0]["url"], caption="Нейросеть: Dall-e 2")


# ======================================================================================================================
#                                             Реф ссылка
# ======================================================================================================================
async def get_ref(call: types.CallbackQuery):
    link = await create_start_link(bot, str(call.from_user.id), encode=True)
    await bot.edit_message_text(f"<b>Ваша реферальная ссылка:</b>\n{link}\n\n"
                                f"Поделитесь ей вашим друзьям и получите <b>бонус</b> 💲. "
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


async def requisites(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text('Напишите мне ваши реквизиты, куда вам было бы удобно вывести ваш бонус.\n'
                                'Это может быть, номер карты, номер телефона (для СБП).'
                                'Данную информацию можно указать с пояснением (пример: +79991112244 '
                                'сбербанк Иванов И.И.)',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_back_to_ref)
    await state.set_state(StateBot.banking_details_input)


async def get_the_money(call: types.CallbackQuery, state: FSMContext):
    balans = await get_balans(call.from_user.id)
    await bot.edit_message_text(f"Ваш баланс: {balans}\n\nНапишите сумму для вывода",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=inline_back_to_ref)
    await state.set_state(StateBot.bonus_output)


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
        request_img = request = None
        if result:
            request, request_img = result
        # ===========================================================================================================
        #                                             Профиль
        # ===========================================================================================================
        if text in ['👤 Ваш профиль']:
            profile_text = await profile(user_id)
            try:
                await message.answer(profile_text, reply_markup=menu_profile)
            except Exception as e:
                print(f"User id: {user_id}\nПрофиль пуст")
        # ============================================================================================================
        #                                             Нейросеть
        # ============================================================================================================
        elif text in ['🔮 Нейросети']:
            await message.answer('<b>Теперь можете переключить нейросеть для ваших дальнейших запросов к боту</b>',
                                 reply_markup=menu_ai)
        # =============================================================================================================
        #                                             Создать чат
        # =============================================================================================================
        elif text in ['🪄 Новая тема']:
            await new_chat(user_id)
            await set_state_ai(user_id, 'gpt')
            await message.answer("Новый чат создан! Теперь вы можете начать диалог на новую тему.",
                                 reply_markup=menu_keyboard)
        # =============================================================================================================
        #                                             Любой запрос к боту
        # =============================================================================================================
        else:
            state_ai = await get_state_ai(user_id)

            if state_ai == 'Ожидание суммы для вывода':
                # text_request = await profile(user_id, 1)
                # balans = await get_balans(user_id)
                # if balans == 0:
                #     await message.answer(f"К сожалению вам пока ничего выводить, ваш баланс: <b>{balans}</b>",
                #                          reply_markup=inline_back_to_ref)
                # if balans >= int(text):
                #     await bot.send_message(6280608864, f'<b>Заявка на вывод бонуса:\n\n{text_request}\n\n'
                #                                        f'На сумму</b>: {text}')
                # else:
                #     await message.answer(f"Вы указали некорректную сумму, ваш баланс: <b>{balans}</b>",
                #                          reply_markup=inline_back_to_ref)
                await set_state_ai(user_id, 'gpt')

            elif state_ai == 'gpt':
                if request != 0:
                    user_question = message.text
                    print(f"Запрос пользователя: {user_question}")
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    processing_message = await message.answer(random.choice(Metadata.options))

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
                    print(f"OpenAI ответ: {response}")

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
                if state_ai == 'dalle2':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(Metadata.options))

                    await send_image(message)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)

                elif state_ai == 'kandinsky3_0':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(Metadata.options))

                    media = await media_group_img(message)
                    await bot.send_media_group(user_id, media)

                    if request_img > 0:
                        await update_requests(user_id, request, request_img - 1)

                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=message_animation.chat.id,
                                             message_id=message_animation.message_id)

                elif state_ai == 'kandinsky2_2':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    message_animation = await message.answer(random.choice(Metadata.options))

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
