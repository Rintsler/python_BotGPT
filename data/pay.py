from aiogram import types
from aiogram.types import LabeledPrice

from data.config import bot, YOOTOKEN
from nav.keyboard import inline_gen_text, inline_gen_post, inline_gen_img, inline_itog, inline_pay

CHECK = [0, 0, 0]


# ======================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "СТАРТ"
# ======================================================================================================================
async def order_submit(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer('Какие функции включить в вашу подписку?\n')
    await call.message.answer('Генерация текста\n', reply_markup=inline_gen_text)
    await call.message.answer('Генерация постов\n', reply_markup=inline_gen_post)
    await call.message.answer('Генерация изображений\n', reply_markup=inline_gen_img)
    await call.message.answer('Для итоговой суммы за подписку нажмите кнопку.\n', reply_markup=inline_itog)


async def order_gen_text(call: types.CallbackQuery):
    if call.message:
        if call.data == "gen_text":
            text = call.message.text + "\n✓  Генерация текста\n"
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)

            CHECK[0] = 500


async def order_gen_img(call: types.CallbackQuery):
    if call.message:
        if call.data == "gen_img":
            text = call.message.text + "\n✓  Генерация изображений\n"
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)
            CHECK[1] = 1000


async def order_gen_post(call: types.CallbackQuery):
    if call.message:
        if call.data == "gen_post":
            text = call.message.text + "\n✓  Генерация постов\n"
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)
            CHECK[2] = 2000


async def order_itog(call: types.CallbackQuery):
    await call.message.answer(f'Сумма к оплате составила:\n{sum(CHECK)}', reply_markup=inline_pay)


# ===================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "КОМФОРТ"
# ===================================================================================================================
async def order(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title='Оформление подписки',
        description='6 мес',
        payload='month_sub',
        provider_token=YOOTOKEN,
        currency='RUB',
        prices=[LabeledPrice(label='Генерация текста', amount=int(sum(CHECK) * 100))],
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
#
#
# # ===================================================================================================================
# #                                            ВЫБОР ПОДПИСКИ "ПРОФИ"
# # ===================================================================================================================
# async def order_pro(call: types.CallbackQuery):
#     await bot.delete_message(call.from_user.id, call.message.message_id)
#     await bot.send_invoice(
#         chat_id=call.from_user.id,
#         title='Оформление подписки',
#         description='Год',
#         payload='month_sub',
#         provider_token=YOOTOKEN,
#         currency='RUB',
#         prices=[
#             LabeledPrice(label='Генерация текста', amount=10000),
#             LabeledPrice(label='Генерация изображений"', amount=45000),
#             LabeledPrice(label='Генерация постов', amount=100000)
#         ],
#         max_tip_amount=30000,
#         suggested_tip_amounts=[5000, 10000, 15000, 20000],
#         start_parameter='test_bot',
#         provider_data=None,
#         # photo_url='https://i.ibb.co/zGw5X0B/image.jpg',
#         photo_size=100,
#         photo_width=800,
#         photo_height=450,
#         need_name=False,
#         need_phone_number=False,
#         need_email=False,
#         need_shipping_address=False,
#         send_phone_number_to_provider=False,
#         send_email_to_provider=False,
#         is_flexible=False,
#         disable_notification=False,
#         protect_content=False,
#         reply_to_message_id=None,
#         allow_sending_without_reply=True,
#         reply_markup=None,
#         request_timeout=15
#     )
#     user.subscribe = 3
