from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

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
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

# Клавиатура с кнопками и настройками размера
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👤 Регистрация"),
            KeyboardButton(text="👥 Создать чат")
        ]
    ],
    resize_keyboard=True
)

# # Новая клавиатура с вариантами подписок
# subscription_keyboard = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="Старт")],
#         [KeyboardButton(text="Комфорт")],
#         [KeyboardButton(text="Профи")],
#     ],
#     resize_keyboard=True
# )

# InLine Buttons подписки
inline_markup_submit = InlineKeyboardMarkup(row_width=3)

start = InlineKeyboardButton(text="Старт", callback_data="start")
komf = InlineKeyboardButton(text="Комфорт", callback_data="komf")
pro = InlineKeyboardButton(text="Профи", callback_data="pro")

inline_markup_submit.insert(start)
inline_markup_submit.insert(komf)
inline_markup_submit.insert(pro)
