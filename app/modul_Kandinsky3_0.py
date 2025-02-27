import asyncio
from aiogram import types
import requests
import json
import base64


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

    async def generate(self, prompt, model, style, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "style": style,
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


async def send_image_kandinsky(message: types.Message, text, style):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '81BECD65C781605F64967084F161012B',
                        'A6B1748E5079BFE4B1F9CBC6A3EB4F50')
    model_id = await api.get_model()
    uuid = await api.generate(text, model_id, style)
    images = await api.check_generation(uuid)
    image = images[0]

    # Декодируем строку base64 в бинарные данные
    image_data = base64.b64decode(image)

    with open(f"image_Kandinsky3_0/{message.from_user.id}+{style}.jpg", "wb") as file:
        file.write(image_data)


