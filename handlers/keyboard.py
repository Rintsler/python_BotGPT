from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ParseMode

# Новая клавиатура с вариантами подписок
subscription_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")],
        [KeyboardButton(text="Комфорт")],
        [KeyboardButton(text="Профи")],
    ],
    resize_keyboard=True
)

#Клавиатура с кнопками и настройками размера
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👤 Регистрация"),
            KeyboardButton(text="❓ HELP")
        ],
        [
            KeyboardButton(text="💰 Подписка"),
            KeyboardButton(text="📝 Токены")
        ]
    ],
    resize_keyboard=True
)