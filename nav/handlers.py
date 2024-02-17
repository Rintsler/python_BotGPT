from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from data.config import bot
from data.controllers import start_cmd, echo, submit, back_to_profile, tp, bot_dialog, check_sub, delle_2, delle_3, \
    Light, Middle, Full, month, month_6, year, cancel_payment, back_to_subscriptions, kandinsky
from data.db_app import update_subscribe
from data.metadata import Metadata
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

router.callback_query.register(kandinsky, F.data == 'kandinsky')
router.callback_query.register(delle_2, F.data == 'delle_2')
router.callback_query.register(delle_3, F.data == 'delle_3')
router.callback_query.register(bot_dialog, F.data == 'bot_dialog')

router.callback_query.register(back_to_profile, F.data == 'back_to_profile')
router.callback_query.register(back_to_subscriptions, F.data == 'back_to_subscriptions')
router.callback_query.register(cancel_payment, F.data == 'cancel_payment')


# ======================================================================================================================
#                                            УСПЕШНАЯ ОПЛАТА
# ======================================================================================================================
# Декоратор - ответ сервису на наличие товара
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_pay(message: types.Message):
    user_id = message.from_user.id
    sub_date = datetime.now().date()
    sub_date_end = ''

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
        await update_subscribe(2, sub_date, sub_date_end, request, request_img, Metadata.sub_period, user_id)
    elif Metadata.subscription == 'Middle':
        request = -1
        request_img = 40
        await update_subscribe(3, sub_date, sub_date_end, request, request_img, Metadata.sub_period, user_id)
    elif Metadata.subscription == 'Premium':
        request = -1
        request_img = -1
        await update_subscribe(4, sub_date, sub_date_end, request, request_img, Metadata.sub_period, user_id)

    response_text = f'Вы подключили тариф {Metadata.subscription}, он будет действовать до {sub_date_end}. Спасибо!'
    await message.answer(response_text, reply_markup=menu_keyboard)


router.message.register(echo)
