import asyncio
import json
import time
import base64
import requests
from aiogram import types
from aiogram.types import FSInputFile

from data.config import bot


class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    async def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    async def generate(self, prompt, model, images=1, width=1024, height=1024, style=3):
        styles = ["KANDINSKY", "UHD", "ANIME", "DEFAULT"]
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "style": styles[style],
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    async def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            await asyncio.sleep(delay)


async def send_image_kandinsky(message: types.Message, text, chat_id):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '81BECD65C781605F64967084F161012B',
                        'A6B1748E5079BFE4B1F9CBC6A3EB4F50')
    model_id = await api.get_model()
    uuid = await api.generate(text, model_id, style=3)
    images = await api.check_generation(uuid)
    image_base64 = images[0]  # Вставьте вашу строку base64 сюда

    # Декодируем строку base64 в бинарные данные

    image_data = base64.b64decode(image_base64)

    with open(f"{message.from_user.id}.jpg", "wb") as file:
        file.write(image_data)

    photo = FSInputFile(f"{message.from_user.id}.jpg")
    # Отправляем изображение в сообщении
    await message.answer_photo(photo, caption="Нейросеть: Kandinsky")

