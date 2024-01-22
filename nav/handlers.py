from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from data.config import bot
from data.controllers import start_cmd, send_image, echo, registration
from data.db_app import update_subscribe
from data.pay import order_st, order_komf, order_pro, user
from aiogram import types
from datetime import datetime
from nav.keyboard import menu_keyboard

router: Router = Router()

router.message.register(start_cmd, CommandStart())
router.message.register(send_image, Command('dalle'))
router.callback_query.register(registration, F.data == 'reg')
router.callback_query.register(order_st, F.data == 'st')
router.callback_query.register(order_komf, F.data == 'komf')
router.callback_query.register(order_pro, F.data == 'pro')


# ======================================================================================================================
#                                            УСПЕШНАЯ ОПЛАТА
# ======================================================================================================================
@router.message(F.successful_payment)
async def successful_pay(message: types.Message):
    user_id = message.from_user.id
    sub_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    tokens = 0

    if user.subscribe == 'Старт':
        tokens = 10000
    elif user.subscribe == 'Комфорт':
        tokens = 50000
    elif user.subscribe == 'Профи':
        tokens = 100000

    await update_subscribe(user.subscribe, sub_date, tokens, user_id)

    response_text = f'Вы выбрали подписку тариф {user.subscribe}. Вам доступно {tokens} токенов. Спасибо!'
    await message.answer(response_text, reply_markup=menu_keyboard)


# Декоратор - ответ сервису на наличие товара
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


router.message.register(echo)
