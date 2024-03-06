from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# ======================================================================================================================
# Buttons основное меню
# ======================================================================================================================
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Ваш профиль")],
        [
            KeyboardButton(text="🪄 Новая тема"),
            KeyboardButton(text="🔮 Нейросети")
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Buttons меню профиля
# ======================================================================================================================
menu_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💰 Подписка", callback_data='submit')],
        [InlineKeyboardButton(text="🛠 Техподдержка", callback_data='tp')],
        [InlineKeyboardButton(text="🤝 Партнерская программа", callback_data='invite_prog')]
    ],
    resize_keyboard=True
)
# ======================================================================================================================
# InLine Buttons меню рефералки
# ======================================================================================================================
menu_profile_ref = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👬 Пригласить друга", callback_data='invite')],
        [InlineKeyboardButton(text="💳 Добавить реквизиты для получения бонуса", callback_data='requisites')],
        [InlineKeyboardButton(text="💰 Вывести бонус", callback_data='get_the_money')],
        [InlineKeyboardButton(text="← назад", callback_data='back_to_profile')]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# Выбор нейронки
# ======================================================================================================================
menu_ai = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🏞 Kandinsky 3.0", callback_data='kandinsky3_0'),
            InlineKeyboardButton(text="🏞 Kandinsky 2.2", callback_data='kandinsky2_2')
        ],
        [
            InlineKeyboardButton(text="🏞 Dell-e 2", callback_data='delle_2'),
            InlineKeyboardButton(text="🏞 Dell-e 3", callback_data='delle_3')
        ],
        [
            InlineKeyboardButton(text="🏞 Обработка изображения", callback_data='novita_img2img'),
        ],
        [
            InlineKeyboardButton(text="📝 Текстовый диалог с Ботом", callback_data='bot_dialog')
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Buttons в меню Подписка
# ======================================================================================================================
inline_submit_preview = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Базовый", callback_data='Light')],
        [InlineKeyboardButton(text="Расширенный", callback_data='Middle')],
        [InlineKeyboardButton(text="👑 Премиум", callback_data='Full')],
        [InlineKeyboardButton(text="← назад", callback_data='back_to_profile')]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Buttons Оплата
# ======================================================================================================================
inline_kb_pay = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Оплатить", pay=True),
            InlineKeyboardButton(text="✖️ Отмена", callback_data='cancel_payment')
        ]
    ],
    resize_keyboard=True
)
# ======================================================================================================================
# InLine Buttons назад в Профиль
# ======================================================================================================================
inline_tp = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="← назад", callback_data='back_to_profile')]
    ],
    resize_keyboard=True
)
# ======================================================================================================================
# InLine Buttons назад в партнерку
# ======================================================================================================================
inline_back_to_ref = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="← назад", callback_data='back_to_ref')]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Button подписка на канал
# ======================================================================================================================
inline_markup_reg = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='👤 Перейти в канал', url='https://t.me/+Myoz4F6P9c9hYTIy')],
        [InlineKeyboardButton(text='✔️ Готово', callback_data="reg")]
    ],
    resize_keyboard=True
)
# ======================================================================================================================
# InLine Button оплата с бонусом
# ======================================================================================================================
inline_Pay_b_m = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='💳 Оплатить картой', callback_data="money_in_pay")],
        [InlineKeyboardButton(text='🗳 Использовать бонус', callback_data="bonus_in_pay")],
        [InlineKeyboardButton(text="✖️ Отмена", callback_data='cancel_payment')]
    ],
    resize_keyboard=True
)
