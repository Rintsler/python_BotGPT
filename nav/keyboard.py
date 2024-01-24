from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import operator

from aiogram_dialog.widgets.kbd import Multiselect
from aiogram_dialog.widgets.text import Format

menu_keyboard_free = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Тарифы"),
            KeyboardButton(text="⚙️ HELP"),
        ],
        [
            # KeyboardButton(text="📝 Остаток запросов"),
            KeyboardButton(text="👥 Создать чат")
        ]
    ],
    resize_keyboard=True
)

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
# ======================================================================================================================
# InLine Buttons подписки
# ======================================================================================================================
inline_markup_submit = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Оформить подписку", callback_data='submit'),
            # InlineKeyboardButton(text="Комфорт", callback_data="komf"),
            # InlineKeyboardButton(text="Профи", callback_data="pro")
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# InLine Button регистрация
# ======================================================================================================================
inline_markup_reg = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='👤 Регистрация', callback_data="reg")
        ]
    ],
    resize_keyboard=True
)

# ======================================================================================================================
# ЧЕК-БОКСЫ
# ======================================================================================================================

inline_gen_text = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Генерация текста", callback_data="gen_text")
        ]
    ],
    resize_keyboard=True
)

inline_gen_post = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Генерация постов", callback_data="gen_post")
        ]
    ],
    resize_keyboard=True
)

inline_gen_img = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Генерация изображения", callback_data="gen_img")
        ]
    ],
    resize_keyboard=True
)

inline_itog = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Расчитать стоимость", callback_data="itog")
        ]
    ],
    resize_keyboard=True
)

inline_pay = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Оплатить", callback_data="pay")
        ]
    ],
    resize_keyboard=True
)
