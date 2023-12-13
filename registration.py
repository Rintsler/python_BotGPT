from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from reg import register

from main import dp


@dp.message_handler(commands=['register'])
async def bot_register(message: types.Message):
    name = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'{message.from_user.first_name}')
            ],
            [
                KeyboardButton(text='Отменить регистрацию')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(f'Привет!\n'
                         f'Для регистрации введи своё имя:',
                         reply_markup=name)
    await register.name.set()


@dp.message_handler(state=register.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    phone = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отменить регистрацию')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        f'<b>{message.text}</b>, теперь пришли мне свой номер телефона чтобы мы могли связаться с тобой',
        reply_markup=phone)
    await register.name.set()


@dp.message_handler(state=register.phone)
async def get_phone(message: types.Message, state: FSMContext):
    answer = message.text
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(test='Отменить регистрацию')
            ]
        ],
        resize_keyboard=True
    )
    try:
        if answer.replace('+', '').isnumeric():
            await state.update_data(phone=answer)
            await message.answer(f'Теперь придумай пароль', reply_markup=markup)
            await register.password.set()
        else:
            await message.answer('Введите корректный номер телефона.', reply_markup=markup)
    except Exception:
        await message.answer('Введите корректный номер телефона.', reply_markup=markup)


@dp.message_handler(state=register.password)
async def get_phone(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(password=answer)
    data = await state.get_data()
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')
    await message.answer(f'Регистрация успешна! \n'
                         f'Имя:{name}\n'
                         f'Телефон:{phone}\n'
                         f'Пароль:{password}\n')
