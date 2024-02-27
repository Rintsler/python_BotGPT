from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from app.moduls import bonus_in_pay, money_in_pay, successful_pay
from data.config import bot
from data.controllers import (start_cmd, echo, submit, back_to_profile, tp, bot_dialog, check_sub, delle_2, delle_3,
                              Light, Middle, Full, month, month_6, year, cancel_payment, back_to_subscriptions,
                              for_kandinsky2_2, get_ref, ref_program, requisites, get_the_money,
                              kandinsky3_0)
from data.db_app import update_subscribe, update_balans
from data.metadata import Metadata
from aiogram import types
from datetime import datetime
from nav.keyboard import menu_keyboard

router: Router = Router()
router.message.register(start_cmd, CommandStart())

router.callback_query.register(check_sub, F.data == 'reg')
router.callback_query.register(submit, F.data == 'submit')
router.callback_query.register(ref_program, F.data == 'invite_prog')
router.callback_query.register(get_ref, F.data == 'invite')
router.callback_query.register(requisites, F.data == 'requisites')
router.callback_query.register(get_the_money, F.data == 'get_the_money')
router.callback_query.register(bonus_in_pay, F.data == 'bonus_in_pay')
router.callback_query.register(money_in_pay, F.data == 'money_in_pay')

router.callback_query.register(Light, F.data == 'Light')
router.callback_query.register(Middle, F.data == 'Middle')
router.callback_query.register(Full, F.data == 'Full')

router.callback_query.register(month, F.data == 'month')
router.callback_query.register(month_6, F.data == 'month_6')
router.callback_query.register(year, F.data == 'year')

router.callback_query.register(tp, F.data == 'tp')

router.callback_query.register(kandinsky3_0, F.data == 'kandinsky3_0')
router.callback_query.register(for_kandinsky2_2, F.data == 'kandinsky2_2')
router.callback_query.register(delle_2, F.data == 'delle_2')
router.callback_query.register(delle_3, F.data == 'delle_3')
router.callback_query.register(bot_dialog, F.data == 'bot_dialog')

router.callback_query.register(back_to_profile, F.data == 'back_to_profile')
router.callback_query.register(back_to_subscriptions, F.data == 'back_to_subscriptions')
router.callback_query.register(ref_program, F.data == 'back_to_ref')
router.callback_query.register(cancel_payment, F.data == 'cancel_payment')


# ======================================================================================================================
#                                            УСПЕШНАЯ ОПЛАТА
# ======================================================================================================================
# Декоратор - ответ сервису на наличие товара
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def pay_end(message: types.Message):
    await successful_pay(message.from_user.id)


router.message.register(echo)
