# -*- coding: utf-8 -*-
import logging
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
import openai

load_dotenv()

os.environ['https_proxy'] = 'https://xzistq:V6m3IYJgdt@45.8.253.142:50100'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=str(os.getenv('6612241633:AAEXsFrv8UveeeDyWuziyVfquC2_HsFREeg')))
dp = Dispatcher(bot)

openai.api_key = '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'

admins_id = [
    6280608864,
    1710996389
]
