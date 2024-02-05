# from aiogram import types
# from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
# from data.config import bot
#
# CHECK = [0, 0, 0]
# TEXT = ["", "", ""]
#
#
# # ======================================================================================================================
# #                                            ВЫБОР ПОДПИСКИ "СТАРТ"
# # ======================================================================================================================
# async def order_submit(call: types.CallbackQuery):
#     if CHECK[0] != 0:
#         TEXT[0] = "✓  Генерация текста"
#     else:
#         TEXT[0] = "Генерация текста"
#     if CHECK[1] != 0:
#         TEXT[1] = "✓  Генерация постов"
#     else:
#         TEXT[1] = "Генерация постов"
#     if CHECK[2] != 0:
#         TEXT[2] = "✓  Генерация изображений"
#     else:
#         TEXT[2] = "Генерация изображений"
#     await call.message.answer('Какие функции включить в вашу подписку?\n'
#                               'Для итоговой суммы за подписку нажмите кнопку.\n',
#                               reply_markup=InlineKeyboardMarkup(
#                                   inline_keyboard=[
#                                       [
#                                           InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
#                                       ],
#                                       [
#                                           InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
#                                       ],
#                                       [
#                                           InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
#                                       ],
#                                       [
#                                           InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
#                                       ]
#                                   ],
#                                   resize_keyboard=False
#                               ))
#     await bot.delete_message(call.from_user.id, call.message.message_id)
#
#
# async def order_gen(call: types.CallbackQuery):
#     if call.message:
#         if call.data == "gen_text":
#             if CHECK[0] == 0:
#                 TEXT[0] = "✓  Генерация текста"
#                 CHECK[0] = 500
#             else:
#                 TEXT[0] = "Генерация текста"
#                 CHECK[0] = 0
#             await call.message.answer(
#                 'Какие функции включить в вашу подписку?\n', reply_markup=InlineKeyboardMarkup(
#                     inline_keyboard=[
#                         [
#                             InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
#                         ],
#                         [
#                             InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
#                         ],
#                         [
#                             InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
#                         ],
#                         [
#                             InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
#                         ]
#                     ],
#                     resize_keyboard=False
#                 ))
#
#         if call.data == "gen_post":
#             if CHECK[1] == 0:
#                 TEXT[1] = "✓  Генерация постов"
#                 CHECK[1] = 1000
#             else:
#                 TEXT[1] = "Генерация постов"
#                 CHECK[1] = 0
#             await call.message.answer(
#                 'Какие функции включить в вашу подписку?\n', reply_markup=InlineKeyboardMarkup(
#                     inline_keyboard=[
#                         [
#                             InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
#                         ],
#                         [
#                             InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
#                         ],
#                         [
#                             InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
#                         ],
#                         [
#                             InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
#                         ]
#                     ],
#                     resize_keyboard=False
#                 ))
#
#         if call.data == "gen_img":
#             if CHECK[2] == 0:
#                 TEXT[2] = "✓  Генерация изображений"
#                 CHECK[2] = 2000
#             else:
#                 TEXT[2] = "Генерация изображений"
#                 CHECK[2] = 0
#             await call.message.answer(
#                 'Какие функции включить в вашу подписку?\n', reply_markup=InlineKeyboardMarkup(
#                     inline_keyboard=[
#                         [
#                             InlineKeyboardButton(text=TEXT[0], callback_data='gen_text')
#                         ],
#                         [
#                             InlineKeyboardButton(text=TEXT[1], callback_data="gen_post")
#                         ],
#                         [
#                             InlineKeyboardButton(text=TEXT[2], callback_data="gen_img")
#                         ],
#                         [
#                             InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
#                         ]
#                     ],
#                     resize_keyboard=False
#                 ))
#     await bot.delete_message(call.from_user.id, call.message.message_id)
#
#
# # async def order_itog(call: types.CallbackQuery):
# #     await bot.delete_message(call.from_user.id, call.message.message_id)
# #     await call.message.answer(f'Сумма к оплате составила:\n{sum(CHECK)}', reply_markup=inline_pay)
