from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_menu_return = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='/menu')
        ]
    ],
    resize_keyboard=True
)
