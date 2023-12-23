import logging
import os

import openai
from aiogram import Bot, Dispatcher

os.environ['https_proxy'] = 'https://xzistq:V6m3IYJgdt@176.106.60.216:50100'
API_TOKEN = '6612241633:AAEXsFrv8UveeeDyWuziyVfquC2_HsFREeg'
OPENAI_API_KEY = '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'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

openai.api_key = OPENAI_API_KEY

admins_id = [
    6280608864
]
