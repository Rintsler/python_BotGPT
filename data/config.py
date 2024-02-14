import logging
import os
import openai
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

chat_id = '-1001998602743'


os.environ['HTTP_PROXY'] = "http://xzistq:V6m3IYJgdt@176.106.61.193:50100"
os.environ['HTTPS_PROXY'] = "http://xzistq:V6m3IYJgdt@176.106.61.193:50100"

# print(requests.get("https://api.ipify.org").text)

SQLALCHEMY_URL = "sqlite+aiosqlite:///db.sqlite3"

# BOT_TOKEN = '6612241633:AAEXsFrv8UveeeDyWuziyVfquC2_HsFREeg'
BOT_TOKEN = '6384872240:AAFeFBDTmyE-LRKPU4Dwl5PUTNtIwV5pA4Y'
OPENAI_API_KEY = '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'
YOOTOKEN = '390540012:LIVE:46409'

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)

openai.api_key = OPENAI_API_KEY

admins_id = [
    6280608864
]
