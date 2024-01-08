from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

menu_keyboard_free = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Информация по подписке"),
            KeyboardButton(text="⚙️ HELP"),
        ],
        [
            KeyboardButton(text="📝 Остаток запросов"),
            KeyboardButton(text="👥 Создать чат"),
        ]
    ],
    resize_keyboard=True
)

# Клавиатура с кнопками и настройками размера
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💰 Подписка"),
            KeyboardButton(text="⚙️ HELP"),
            KeyboardButton(text="📊 Профиль")
        ],
        [
            KeyboardButton(text="📝 Токены"),
            KeyboardButton(text="👥 Создать чат"),
        ]
    ],
    resize_keyboard=True
)

# InLine Buttons подписки
inline_markup_submit = InlineKeyboardMarkup(row_width=3)

st = InlineKeyboardButton(text="Старт", callback_data="st")
komf = InlineKeyboardButton(text="Комфорт", callback_data="komf")
pro = InlineKeyboardButton(text="Профи", callback_data="pro")

inline_markup_submit.insert(st)
inline_markup_submit.insert(komf)
inline_markup_submit.insert(pro)

inline_markup_reg = InlineKeyboardMarkup(row_width=1)

reg = InlineKeyboardButton(text="👤 Регистрация", callback_data="reg")
inline_markup_reg.insert(reg)
