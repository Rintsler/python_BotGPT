import logging
import os
import requests
import openai
from aiogram import Bot, Dispatcher
from aiogram.client.session import aiohttp
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import asyncio

# PROXY_END_POINT = '176.106.61.193:50100'
# USERNAME = 'xzistq'
# PASSWORD = 'V6m3IYJgdt'
#
#
# async def get_response_using_proxy():
#     async with aiohttp.ClientSession() as session:
#         async with session.get(
#                 'https://ip.oxylabs.io/',
#                 proxy=f'http://{USERNAME}:{PASSWORD}@{PROXY_END_POINT}'
#         ) as response:
#             print('Status Code: ', response.status)
#             print('Body: ', await response.text())
#
#
# loop_obj = asyncio.get_event_loop()
# loop_obj.run_until_complete(get_response_using_proxy())

chat_id = '-1001998602743'


os.environ['HTTP_PROXY'] = "http://xzistq:V6m3IYJgdt@176.106.61.193:50100"
os.environ['HTTPS_PROXY'] = "http://xzistq:V6m3IYJgdt@176.106.61.193:50100"

# URL, который вы хотите запросить
url = "https://api.ipify.org"

# Создание словаря с настройками прокси
proxies = {
    "http": os.environ['HTTP_PROXY'],
    "https": os.environ['HTTP_PROXY']
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
# print(requests.get("https://api.ipify.org").text)

SQLALCHEMY_URL = "sqlite+aiosqlite:///db.sqlite3"

# BOT_TOKEN = '6612241633:AAEXsFrv8UveeeDyWuziyVfquC2_HsFREeg'
BOT_TOKEN = '6384872240:AAFeFBDTmyE-LRKPU4Dwl5PUTNtIwV5pA4Y'
OPENAI_API_KEY = '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'
YOOTOKEN = '390540012:LIVE:46409'

# тест
# YOOTOKEN = '381764678:TEST:77854'

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)

openai.api_key = OPENAI_API_KEY

admins_id = [
    6280608864
]
