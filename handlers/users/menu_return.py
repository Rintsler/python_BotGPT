from aiogram import types
from aiogram.dispatcher.filters import Command

from keyboards.default import kb_menu_return
from loader import dp


@dp.message_handler(Command('Возврат в главное меню'))
async def menu_return(message: types.Message):
    await message.answer(f'Привет {message.from_user.full_name}!\n'
                         f'Возвращаем тебя в главное меню', reply_markup=kb_menu_return)
