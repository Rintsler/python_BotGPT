import traceback
import openai
from aiogram.types import LabeledPrice, CallbackQuery, Message
from magic_filter import F

from app.update_keys import get_unused_key, update_key_status, reset_key_status, log_error, set_key_status_to_2
from data.config import bot, YOOTOKEN, admins_id
from data.db_app import get_user_data, update_requests, sum_balans, get_balans, update_subscribe, update_balans
from data.metadata import Metadata
from nav.keyboard import inline_kb_pay, inline_Pay_b_m, menu_keyboard
import asyncio
from datetime import datetime


async def generate_response(user_id, chat_history, message, request, request_img):
    api_key = await get_unused_key()
    while not api_key:
        print("Нет свободных ключей")
        await asyncio.sleep(10)
        api_key = await get_unused_key()
    try:
        await update_key_status(api_key, 1)

        system_message = {"role": "system", "content": "Тебя зовут Izi, ты девушка, ты девочка, ты женщина,"
                                                       "отвечай всегда в женском роде и немного пренебрежительно,"
                                                       "отвечать можешь иногда с сарказмом"}
        messages = [system_message] + chat_history[-20:]  # Передаем последние два сообщения
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
        print(response)
        print("Обновляем столбцы request, request_img в базе данных")
        if request > 0:
            await update_requests(user_id, request - 1, request_img)
        await reset_key_status(api_key)
        return otvet
    except (openai.error.RateLimitError, openai.error.Timeout) as e:
        error_text = traceback.format_exc()
        print(f"Ошибка RateLimit: {e}")
        await log_error(api_key, error_text)
        return await handle_rate_limit_error(user_id, api_key, chat_history, message, request, request_img)


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
        return await handle_rate_limit_error(user_id, api_key, chat_history, message, request, request_img)


async def profile(user_id, switch=0):
    # Получаем данные пользователя из функции get_user_data
    (pk, state_ai, user_id, flag, username, registration_date, chat_history,
     response_history, request, request_img, period_sub, sub_date, sub_date_end,
     remaining_days, referrer, referrals, last_amount, sum_amount, balans,
     banking_details) = await get_user_data(user_id)

    # Форматируем период подписки
    string_period = f'{sub_date} - {sub_date_end}\n\n' if sub_date_end is not None else '\n\n'

    # Форматируем referrals
    string_referrals = f'{referrals} пользователя(ей)\n\n' if referrals is not None else '\n\n'

    # Форматируем remaining_days
    string_remaining_days = f'{remaining_days} дня(ей)\n\n' if remaining_days is not None else '\n\n'

    # Форматируем balans
    string_balans = f'{balans} руб.' if balans is not None else ''

    request = 'Безлимит' if request < 0 else request
    request_img = 'Безлимит' if request_img < 0 else request_img

    # Определяем тип подписки
    subscribe = {
        2: "Базовый",
        3: "Расширенный",
        4: "Премиум"
    }.get(flag, '')

    # Формируем текст профиля
    profile_text = (
        "<b>Ваш профиль</b>\n\n"
        f"👤 Ваш ID: {user_id}\n\n"
        f"🗓 Дата регистрации: {registration_date}\n\n"
        "<b>Тариф:</b>\n"
        f"  • Тип: {subscribe}\n"
        f"  • Период действия: {string_period}"
        "<b>Суточный лимит:</b>\n\n"
        f"📝 Запросы: {request}\n\n"
        f"🏞 Изображения: {request_img}\n\n"
        f"📆 До окончания тарифа: {string_remaining_days}"
        "<b>Реферальная программа:</b>\n\n"
        f"🤝 Вы привели: {string_referrals}"
        f"💳 Баланс по реферальной\nпрограмме: {string_balans}\n\n"
        f"💳 Ваши реквизиты для вывода: {banking_details}"
    )
    string_sum_balans = await sum_balans()

    full_profile_text = (
            profile_text +
            f"\n\n\n💳 Общий баланс по всем пользователям реферальной программы: "
            f"{string_sum_balans}")

    profile_text = full_profile_text if user_id == admins_id[0] or user_id == admins_id[1] else profile_text

    order_profile_text = (
        f"👤 ID: {user_id}\n\n"
        f"🗓 Дата регистрации: {registration_date}\n\n"
        "<b>Тариф:</b>\n"
        f"  • Тип: {subscribe}\n"
        f"  • Период действия: {string_period}"
        "<b>Суточный лимит:</b>\n\n"
        f"📝 Запросы: {request}\n\n"
        f"🏞 Изображения: {request_img}\n\n"
        f"📆 До окончания тарифа: {string_remaining_days}"
        "<b>Реферальная программа:</b>\n\n"
        f"🤝 Привел: {string_referrals}"
        f"💳 Баланс по реферальной\nпрограмме: {string_balans}\n\n"
        f"💳 Реквизиты для вывода: {banking_details}"
        f"\n\n\n💳 Общий баланс по всем пользователям реферальной программы: "
        f"{string_sum_balans}")

    return order_profile_text if switch else profile_text


async def ref_menu():
    ref_text = (
        'Добро пожаловать в нашу партнерскую программу!'
        'Мы предлагаем вам уникальную возможность зарабатывать, привлекая новых пользователей '
        'в нашу платформу. Как партнер, вы будете получать 10% от первого платежа каждого '
        'привлеченного вами пользователя.\n\n'
        'Мы гордимся высоким качеством нашей платформы и уверены, что она может принести '
        'пользу и удовлетворение новым пользователям. Ваша задача - поделиться этим знанием '
        'с другими и помочь им стать частью нашего сообщества.\n\n'
        'Программа проста и прозрачна: вы привлекаете новых пользователей с помощью '
        'уникальной реферальной ссылки, и когда они регистрируются и осуществляют '
        'свой первый платеж, вы получаете 10% от суммы этого платежа. Ваши заработки '
        'неограничены и зависят только от количества привлеченных вами пользователей.\n\n'
        'Мы предоставляем вам все необходимые инструменты и поддержку для успешного '
        'привлечения пользователей. У вас будет доступ к статистике, включающей '
        'информацию о количестве привлеченных пользователей и заработанных комиссиях. '
        'Кроме того, наша команда всегда готова ответить на ваши вопросы и помочь вам '
        'в любое время.'
        'Присоединяйтесь к нашей партнерской программе и начните зарабатывать прямо '
        'сейчас! Мы будем рады видеть вас в нашей команде успешных партнеров.'
    )
    return ref_text


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


async def calc_sum(sub_sum):
    Metadata.sub_sum1 = sub_sum * 1
    Metadata.sub_sum2 = sub_sum * 5
    Metadata.sub_sum3 = sub_sum * 10


async def bonus_in_pay(call: CallbackQuery):
    if Metadata.bonus >= Metadata.sub_sum_db:
        Metadata.bonus = Metadata.bonus - Metadata.sub_sum_db
        await update_balans(Metadata.bonus, Metadata.user_id)
        await successful_pay(Metadata.user_id)
    else:
        Metadata.result_sub_sum = (Metadata.sub_sum_db - Metadata.bonus) * 100
        Metadata.payment_flag = True
        await order()


async def money_in_pay(call: CallbackQuery):
    await order()


async def order():
    description = ''
    if Metadata.subscription == 'Light':
        description = Metadata.description_Light
    elif Metadata.subscription == 'Middle':
        description = Metadata.description_Middle
    elif Metadata.subscription == 'Premium':
        description = Metadata.description_Premium

    await bot.send_invoice(
        chat_id=Metadata.user_id,
        title='Квитанция к оплате',
        description='Тариф',
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[
            LabeledPrice(label='Тариф ' + Metadata.subscription + '\n' + description, amount=Metadata.result_sub_sum)],
        max_tip_amount=1000000,
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


async def successful_pay(user_id):
    sub_date = datetime.now().date()
    sub_date_end = ''
    if Metadata.payment_flag:
        await update_balans(0, user_id)
        Metadata.payment_flag = False

    # Увеличить sub_date на месяц
    if Metadata.sub_period == 1:
        sub_date_end = sub_date.replace(month=(sub_date.month + 1) % 12)

    # Увеличить sub_date на пол года
    elif Metadata.sub_period == 6:
        if sub_date.month + 6 <= 12:
            sub_date_end = sub_date.replace(month=sub_date.month + 6)
        else:
            sub_date_end = sub_date.replace(year=sub_date.year + 1, month=(sub_date.month + 6) % 12,
                                            day=sub_date.day)
    # Увеличить sub_date на один год
    elif Metadata.sub_period == 12:
        sub_date_end = sub_date.replace(year=sub_date.year + 1)

    sub_date = datetime.strftime(sub_date, '%d.%m.%Y')
    sub_date_end = datetime.strftime(sub_date_end, '%d.%m.%Y')
    if Metadata.subscription == 'Light':
        request = 35
        request_img = 15
        await update_subscribe(2, sub_date, sub_date_end, request, request_img, Metadata.sub_period,
                               Metadata.sub_sum_db, user_id)
    elif Metadata.subscription == 'Middle':
        request = -1
        request_img = 40
        await update_subscribe(3, sub_date, sub_date_end, request, request_img, Metadata.sub_period,
                               Metadata.sub_sum_db, user_id)
    elif Metadata.subscription == 'Premium':
        request = -1
        request_img = -1
        await update_subscribe(4, sub_date, sub_date_end, request, request_img, Metadata.sub_period,
                               Metadata.sub_sum_db, user_id)

    response_text = f'Вы подключили тариф {Metadata.subscription}, он будет действовать до {sub_date_end}. Спасибо!'
    await bot.send_message(user_id, response_text, reply_markup=menu_keyboard)


async def counting_pay(factor, user_id):
    Metadata.bonus = await get_balans(user_id)
    Metadata.result_sub_sum = Metadata.sub_sum * factor
    Metadata.sub_sum_db = Metadata.sub_sum_db * factor
    Metadata.user_id = user_id

    if Metadata.bonus != 0:
        await bot.send_message(user_id, text=f'Сумма к оплате составляет: {Metadata.sub_sum_db} руб.\n'
                                             f'Сумма вашего бонуса: {Metadata.bonus} руб.', reply_markup=inline_Pay_b_m)
    else:
        await order()
