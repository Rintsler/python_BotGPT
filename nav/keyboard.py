from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='pay',
            description='Оплата подписки'
        )
    ]


menu_keyboard_free = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Тарифы"),
            KeyboardButton(text="⚙️ HELP"),
        ],
        # [
        #     KeyboardButton(text="📝 Остаток запросов"),
        #     KeyboardButton(text="👥 Создать чат"),
        # ]
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
            InlineKeyboardButton(text="Старт", callback_data="st"),
            InlineKeyboardButton(text="Комфорт", callback_data="komf"),
            InlineKeyboardButton(text="Профи", callback_data="pro")
        ]
    ],
)

# inline_markup_submit = InlineKeyboardMarkup(row_width=3)
#
# st = InlineKeyboardButton(text="Старт", callback_data="st")
# komf = InlineKeyboardButton(text="Комфорт", callback_data="komf")
# pro = InlineKeyboardButton(text="Профи", callback_data="pro")
# inline_markup_submit.add(st, komf, pro)

# ======================================================================================================================
# InLine Button регистрация
# ======================================================================================================================
inline_markup_reg = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='👤 Регистрация', callback_data="reg")
        ]
    ],
)

# inline_markup_reg = InlineKeyboardMarkup(row_width=1)
# reg = InlineKeyboardButton(text="👤 Регистрация", callback_data="reg")
# inline_markup_reg.insert(reg)
