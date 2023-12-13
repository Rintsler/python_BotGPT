import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from reg import register


# Включаем логирование
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6974809974:AAG9dnOZjqjfTpCnjmOng_rAOKCTmKzoO5E")
# Диспетчер
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет!")





# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
