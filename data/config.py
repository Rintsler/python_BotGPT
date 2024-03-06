import logging
import os
import requests
import openai
from aiogram import Bot, Dispatcher
import aiohttp
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

chat_id = '-1001998602743'

os.environ['HTTP_PROXY'] = "http://osmanovolegj:IwcBev2efD@176.106.60.99:50100"
os.environ['HTTPS_PROXY'] = "http://osmanovolegj:IwcBev2efD@176.106.60.99:50100"

# URL, который вы хотите запросить
url = "https://api.ipify.org"

# Создание словаря с настройками прокси
proxies = {
    "http": os.environ['HTTP_PROXY'],
    "https": os.environ['HTTPS_PROXY']
}

try:
    # Выполнение GET-запроса через прокси
    response = requests.get(url, proxies=proxies)

    # Вывод результата подключения
    print("Результат подключения к ПРОКСИ:")
    print(f"Код состояния: {response.status_code}")
    print(f"Текст ответа: {response.text}")

except requests.RequestException as e:
    # Вывод ошибки, если что-то пошло не так
    print(f"Ошибка подключения к ПРОКСИ: {e}")

SQLALCHEMY_URL = "sqlite+aiosqlite:///db.sqlite3"

# ТЕСТ
BOT_TOKEN = '6961722181:AAHb8Djor842kI7oIEkO6GuSzZhMIoimQCM'
# тест
YOOTOKEN = '1744374395:TEST:4f8afe3cb5414f582b71'

# ОРИГИНАЛ
# BOT_TOKEN = '6384872240:AAFeFBDTmyE-LRKPU4Dwl5PUTNtIwV5pA4Y'
OPENAI_API_KEY = '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'
# ОРИГИНАЛ
# YOOTOKEN = '390540012:LIVE:46409'

storage = MemoryStorage()

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY

admins_id = [
    6280608864,
    1710996389
]

