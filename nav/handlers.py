from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from data.config import bot
from data.controllers import start_cmd, echo, submit, back_to_profile, tp, bot_dialog, \
    dalle_3, dalle_2, check_sub
from data.db_app import update_subscribe
from data.pay import order_itog, order, order_gen
from aiogram import types
from datetime import datetime
from nav.keyboard import menu_keyboard

router: Router = Router()
router.message.register(start_cmd, CommandStart())
router.callback_query.register(check_sub, F.data == 'reg')
router.callback_query.register(submit, F.data == 'submit')
router.callback_query.register(tp, F.data == 'tp')
router.callback_query.register(dalle_2, F.data == 'dally_2')
router.callback_query.register(dalle_3, F.data == 'dally_3')
router.callback_query.register(bot_dialog, F.data == 'bot_dialog')
router.callback_query.register(back_to_profile, F.data == 'back_to_profile')

router.callback_query.register(order_gen, F.data == 'gen_text')
router.callback_query.register(order_gen, F.data == 'gen_post')
router.callback_query.register(order_gen, F.data == 'gen_img')
router.callback_query.register(order_itog, F.data == 'itog')
router.callback_query.register(order, F.data == 'pay')


# ======================================================================================================================
#                                            УСПЕШНАЯ ОПЛАТА
# ======================================================================================================================
@router.message(F.successful_payment)
async def successful_pay(message: types.Message):
    user_id = message.from_user.id
    sub_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    tokens = 0
    await update_subscribe(3, sub_date, tokens, user_id)

    response_text = f'Вы выбрали подписку тариф на месяц. Спасибо!'
    await message.answer(response_text, reply_markup=menu_keyboard)


# Декоратор - ответ сервису на наличие товара
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


router.message.register(echo)
