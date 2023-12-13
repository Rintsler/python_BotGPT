from aiogram.dispatcher.filters.state import StatesGroup, State


class register(StatesGroup):
    phone = State()
    name = State()
    password = State()
    tariff = State()
