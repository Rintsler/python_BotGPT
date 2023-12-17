import logging
import openai
import os
from aiogram import Bot, Dispatcher

os.environ['https_proxy'] = 'https://gjnkkgg:Vgjkngubgjjt@65.9.223.112:50100'
API_TOKEN = '1111111111:AAAAAAABBBBBBBBDDDDDDDDCCCCCCCEEEEE'
OPENAI_API_KEY = 'SK-jdjidjdjdjdinfkgkkgkgkkgkgkgngkgkkgkgkkggkk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

openai.api_key = OPENAI_API_KEY
