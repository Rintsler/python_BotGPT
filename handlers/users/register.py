from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from loader import dp
from states import register


@dp.message_handler(Command('register'))
async def register_(message: types.Message):
    await message.answer('Привет, ты начал регистрацию, \nВведи свое имя')
    await register.test1.set()


@dp.message_handler(state=register.test1)
async def state1(message: types.Message, state: FSMContext):
    answer = message.text

    await state.update_data(test1=answer)
    await message.answer('Введи номер телефона')
    await register.test2.set()


@dp.message_handler(state=register.test2)
async def state1(message: types.Message, state: FSMContext):
    answer = message.text

    await state.update_data(test2=answer)
    data = await state.get_data()
    name = data.get('test1')
    phone = data.get('test2')
    await message.answer(f'Регистрация успешна\n'
                         f'Твое имя{name}\n'
                         f'номер: {phone}')
    await state.finish()