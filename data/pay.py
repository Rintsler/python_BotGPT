from datetime import datetime

from aiogram.types import LabeledPrice
from data.bufer import user
from data.config import YOOTOKEN, bot
from aiogram import types

from data.db_app import get_subscribe, update_subscribe
from nav.keyboard import menu_keyboard


# ======================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "СТАРТ"
# ======================================================================================================================
async def order_st(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title='Оформление подписки',
        description='Подписка по тарифу "Старт" - лимит 10000 токенов',
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[LabeledPrice(label='Подписка "Старт"', amount=15000)],
        max_tip_amount=30000,
        suggested_tip_amounts=[5000, 10000, 15000, 20000],
        start_parameter='test_bot',
        provider_data=None,
        # photo_url='https://i.ibb.co/zGw5X0B/image.jpg',
        photo_size=100,
        photo_width=800,
        photo_height=450,
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
        reply_markup=None,
        request_timeout=15
    )
    user.subscribe = "Старт"


# ===================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "КОМФОРТ"
# ===================================================================================================================
async def order_komf(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title='Оформление подписки',
        description='Подписка по тарифу "Старт" - лимит 10000 токенов',
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[LabeledPrice(label='Подписка "Комфорт"', amount=50000)],
        max_tip_amount=30000,
        suggested_tip_amounts=[5000, 10000, 15000, 20000],
        start_parameter='test_bot',
        provider_data=None,
        # photo_url='https://i.ibb.co/zGw5X0B/image.jpg',
        photo_size=100,
        photo_width=800,
        photo_height=450,
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
        reply_markup=None,
        request_timeout=15
    )
    user.subscribe = "Комфорт"


# ===================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "ПРОФИ"
# ===================================================================================================================
async def order_pro(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title='Оформление подписки',
        description='Подписка по тарифу "Старт" - лимит 10000 токенов',
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[LabeledPrice(label='Подписка "Профи"', amount=100000)],
        max_tip_amount=30000,
        suggested_tip_amounts=[5000, 10000, 15000, 20000],
        start_parameter='test_bot',
        provider_data=None,
        # photo_url='https://i.ibb.co/zGw5X0B/image.jpg',
        photo_size=100,
        photo_width=800,
        photo_height=450,
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
        reply_markup=None,
        request_timeout=15
    )
    user.subscribe = "Профи"
