from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура после оплаты
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💰 Подписка"),
            KeyboardButton(text="📊 Профиль"),
        ],
        [
            KeyboardButton(text="📝 Токены"),
            KeyboardButton(text="👥 Создать чат"),
            KeyboardButton(text="⚙️ HELP")
        ]
    ],
    resize_keyboard=True
)

# Клавиатура до оплаты
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⚙️ HELP"),
            KeyboardButton(text="👥 Создать чат"),
            KeyboardButton(text="Запросов осталось")
        ]
    ],
    resize_keyboard=True
)

# InLine Buttons подписки
inline_markup_submit = InlineKeyboardMarkup(row_width=3)

start = InlineKeyboardButton(text="Старт", callback_data="start")
komf = InlineKeyboardButton(text="Комфорт", callback_data="komf")
pro = InlineKeyboardButton(text="Профи", callback_data="pro")

inline_markup_submit.insert(start)
inline_markup_submit.insert(komf)
inline_markup_submit.insert(pro)

# InLine Buttons регистрации
inline_markup_reg = InlineKeyboardMarkup(row_width=1)

reg = InlineKeyboardButton(text="👤 Регистрация", callback_data="reg")

inline_markup_reg.insert(reg)
