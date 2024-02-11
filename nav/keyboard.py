from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from data.metadata import Metadata

# ======================================================================================================================
# InLine Buttons основное меню
# ======================================================================================================================
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Профиль")
        ],
        [
            KeyboardButton(text="🧠 Нейросеть"),
            KeyboardButton(text="👥 Создать чат")
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Buttons меню профиля
# ======================================================================================================================
menu_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Подписка", callback_data='submit')
        ],
        [
            InlineKeyboardButton(text="🛠 Техподдержка", callback_data='tp')
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# Выбор нейронки
# ======================================================================================================================
menu_ai = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Генерация изображения Kandinsky", callback_data='kandinsky')
        ],
        [
            InlineKeyboardButton(text="Генерация изображения Dell-e 2", callback_data='delle_2')
        ],
        [
            InlineKeyboardButton(text="Генерация изображения Dell-e 3", callback_data='delle_3')
        ],
        [
            InlineKeyboardButton(text="Текстовый диалог с Ботом", callback_data='bot_dialog')
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Buttons в меню Подписка
# ======================================================================================================================
inline_submit_preview = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Базовый", callback_data='Light')
        ],
        [
            InlineKeyboardButton(text="Расширенный", callback_data='Middle')
        ],
        [
            InlineKeyboardButton(text="👑 Премиум", callback_data='Full')
        ],
        [
            InlineKeyboardButton(text="← назад", callback_data='back_to_profile')
        ]
    ],
    resize_keyboard=True
)
# ======================================================================================================================
# InLine Buttons в меню подписки - период
# ======================================================================================================================

# inline_submit_period = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             # InlineKeyboardButton(text="Оформить подписку", callback_data='submit_up')
#             InlineKeyboardButton(text=f'Месяц - {Metadata.sub_sum1}', callback_data='month')
#         ],
#         [
#             InlineKeyboardButton(text=f'6 месяцев - {Metadata.sub_sum2}', callback_data='month_6')
#         ],
#         [
#             InlineKeyboardButton(text=f'Год - {Metadata.sub_sum3}', callback_data='year')
#         ],
#         [
#             InlineKeyboardButton(text="← назад", callback_data='back_to_subscriptions')
#         ]
#     ],
#     resize_keyboard=True
# )
# ======================================================================================================================
# InLine Buttons Оплата
# ======================================================================================================================
inline_kb_pay = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Оплатить", pay=True),
            InlineKeyboardButton(text="✖️ Отмена", callback_data='cancel_payment')
        ]
    ]
)
# ======================================================================================================================
# InLine Buttons назад в Профиль
# ======================================================================================================================
inline_tp = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="← назад", callback_data='back_to_profile')
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Button подписка на канал
# ======================================================================================================================
inline_markup_reg = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='👤 Подписаться', url='https://t.me/+Myoz4F6P9c9hYTIy')
        ],
        [
            InlineKeyboardButton(text='✔️ Готово', callback_data="reg")
        ],
    ],
    resize_keyboard=True
)
