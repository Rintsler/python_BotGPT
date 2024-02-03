from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from data.config import bot
from data.controllers import start_cmd, echo, submit, back_to_profile, tp, bot_dialog, check_sub, delle_2, delle_3, \
    Light, Middle, Full, month, month_6, year, cancel_payment, back_to_subscriptions
from data.db_app import update_subscribe
from data.metadata import Metadata
from data.pay import order_gen
from aiogram import types
from datetime import datetime
from nav.keyboard import menu_keyboard

router: Router = Router()
router.message.register(start_cmd, CommandStart())
router.callback_query.register(check_sub, F.data == 'reg')

router.callback_query.register(submit, F.data == 'submit')

router.callback_query.register(Light, F.data == 'Light')
router.callback_query.register(Middle, F.data == 'Middle')
router.callback_query.register(Full, F.data == 'Full')

router.callback_query.register(month, F.data == 'month')
router.callback_query.register(month_6, F.data == 'month_6')
router.callback_query.register(year, F.data == 'year')

router.callback_query.register(tp, F.data == 'tp')

router.callback_query.register(delle_2, F.data == 'delle_2')
router.callback_query.register(delle_3, F.data == 'delle_3')
router.callback_query.register(bot_dialog, F.data == 'bot_dialog')

router.callback_query.register(back_to_profile, F.data == 'back_to_profile')
router.callback_query.register(back_to_subscriptions, F.data == 'back_to_subscriptions')
router.callback_query.register(cancel_payment, F.data == 'cancel_payment')

router.callback_query.register(order_gen, F.data == 'gen_text')
router.callback_query.register(order_gen, F.data == 'gen_post')
router.callback_query.register(order_gen, F.data == 'gen_img')
# router.callback_query.register(order_itog, F.data == 'itog')


# ======================================================================================================================
#                                            УСПЕШНАЯ ОПЛАТА
# ======================================================================================================================
@router.message(F.successful_payment)
async def successful_pay(message: types.Message):
    user_id = message.from_user.id
    sub_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    if Metadata.sub_period == 1:
        request = 35
        request_img = 15
        await update_subscribe(2, sub_date, request, request_img, user_id)
    elif Metadata.sub_period == 6:
        request = -1
        request_img = 40
        await update_subscribe(3, sub_date, request, request_img, user_id)
    elif Metadata.sub_period == 12:
        request = -1
        request_img = -1
        await update_subscribe(4, sub_date, request, request_img, user_id)

    response_text = f'Вы выбрали тариф {Metadata.subscription}. Спасибо!'
    await message.answer(response_text, reply_markup=menu_keyboard)


# Декоратор - ответ сервису на наличие товара
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


router.message.register(echo)
