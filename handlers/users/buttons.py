from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('10'))
async def buttons_test(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Ты выбрал число {message.text}')


@dp.message_handler(Command('11'))
async def buttons_test(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Ты выбрал число {message.text}')


@dp.message_handler(Command('100'))
async def buttons_test(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Ты выбрал число {message.text}')


@dp.message_handler(Command('Подпишись'))
async def buttons_test(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Ты выбрал число {message.text}')


@dp.message_handler(Command('Лайк'))
async def buttons_test(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Ты выбрал число {message.text}')


@dp.message_handler(Command('Меню'))
async def buttons_test(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Ты выбрал число {message.text}')
