from aiogram import types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from data.config import bot
from data.metadata import Metadata
from nav.keyboard import inline_pay

CHECK = [0, 0, 0]
TEXT = ["", "", ""]


# ======================================================================================================================
#                                            ВЫБОР ПОДПИСКИ "СТАРТ"
# ======================================================================================================================
async def order_submit(call: types.CallbackQuery):
    if CHECK[0] != 0:
        TEXT[0] = "✓  Генерация текста"
    else:
        TEXT[0] = "Генерация текста"
    if CHECK[1] != 0:
        TEXT[1] = "✓  Генерация постов"
    else:
        TEXT[1] = "Генерация постов"
    if CHECK[2] != 0:
        TEXT[2] = "✓  Генерация изображений"
    else:
        TEXT[2] = "Генерация изображений"
    await call.message.answer('Какие функции включить в вашу подписку?\n'
                              'Для итоговой суммы за подписку нажмите кнопку.\n',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
                                      ],
                                      [
                                          InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
                                      ],
                                      [
                                          InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
                                      ],
                                      [
                                          InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
                                      ]
                                  ],
                                  resize_keyboard=False
                              ))
    await bot.delete_message(call.from_user.id, call.message.message_id)


async def order_gen(call: types.CallbackQuery):
    if call.message:
        if call.data == "gen_text":
            if CHECK[0] == 0:
                TEXT[0] = "✓  Генерация текста"
                CHECK[0] = 500
            else:
                TEXT[0] = "Генерация текста"
                CHECK[0] = 0
            await call.message.answer(
                'Какие функции включить в вашу подписку?\n', reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
                        ],
                        [
                            InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
                        ],
                        [
                            InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
                        ],
                        [
                            InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
                        ]
                    ],
                    resize_keyboard=False
                ))

        if call.data == "gen_post":
            if CHECK[1] == 0:
                TEXT[1] = "✓  Генерация постов"
                CHECK[1] = 1000
            else:
                TEXT[1] = "Генерация постов"
                CHECK[1] = 0
            await call.message.answer(
                'Какие функции включить в вашу подписку?\n', reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
                        ],
                        [
                            InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
                        ],
                        [
                            InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
                        ],
                        [
                            InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
                        ]
                    ],
                    resize_keyboard=False
                ))

        if call.data == "gen_img":
            if CHECK[2] == 0:
                TEXT[2] = "✓  Генерация изображений"
                CHECK[2] = 2000
            else:
                TEXT[2] = "Генерация изображений"
                CHECK[2] = 0
            await call.message.answer(
                'Какие функции включить в вашу подписку?\n', reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
                        ],
                        [
                            InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
                        ],
                        [
                            InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
                        ],
                        [
                            InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
                        ]
                    ],
                    resize_keyboard=False
                ))
    await bot.delete_message(call.from_user.id, call.message.message_id)


async def order_itog(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer(f'Сумма к оплате составила:\n{sum(CHECK)}', reply_markup=inline_pay)


# ===================================================================================================================
#                                            Ордер к оплате
# ===================================================================================================================
# async def order(call: types.CallbackQuery, label=None):
#     await bot.delete_message(call.from_user.id, call.message.message_id)
#     await bot.send_invoice(
#         chat_id=call.from_user.id,
#         title='Оплата подписки в боте',
#         description=Metadata.sub_period,
#         payload='month_sub',
#         provider_token=SBERTOKEN,
#         currency='RUB',
#         prices=[LabeledPrice(label=label, amount=int(sum(CHECK) * 100))],
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
# #
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
#         provider_token=SBERTOKEN,
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
