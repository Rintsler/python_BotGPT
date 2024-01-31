from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


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
# InLine Buttons меню профиля
# ======================================================================================================================
menu_ai = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Генерация изображения Dally 2", callback_data='dally_2')
        ],
        [
            InlineKeyboardButton(text="Генерация изображения Dally 3", callback_data='dally_3')
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
            InlineKeyboardButton(text="Оформить подписку", callback_data='submit_up')
        ],
        [
            InlineKeyboardButton(text="← назад", callback_data='back_to_profile')
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Buttons в меню Техподдержка
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
            InlineKeyboardButton(text='Готово', callback_data="reg")
        ],
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# ЧЕК-БОКСЫ
# ======================================================================================================================
inline_pay = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Оплатить", callback_data="pay")
        ],
        [
            InlineKeyboardButton(text="← назад", callback_data='back')
        ]
    ],
    resize_keyboard=False
)
