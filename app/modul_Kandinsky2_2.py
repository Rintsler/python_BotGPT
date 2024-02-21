import base64
import io
from aiogram.types import PhotoSize
from aiogram.types import FSInputFile, InputFile
from io import BytesIO, StringIO
from kandinsky2 import get_kandinsky2
from aiogram import types
from PIL import Image

from data.config import bot


async def kandinsky2_2(message: types.Message, text):
    model = get_kandinsky2(
        'cuda',
        task_type='text2img',
        cache_dir='/tmp/kandinsky2',
        model_version='2.1',
        use_flash_attention=False
    )
    images = model.generate_text2img(
        text,
        num_steps=100,
        batch_size=1,
        guidance_scale=4,
        h=768,
        w=768,
        sampler='p_sampler',
        prior_cf_scale=4,
        prior_steps="5"
    )
    image = images[0]  # Вставьте вашу строку base64 сюда

    # Сохраняем изображение в файл
    image.save(f"image_Kandinsky2_2/{message.from_user.id}.jpg")

    photo = FSInputFile(f"image_Kandinsky2_2/{message.from_user.id}.jpg")
    # Отправляем изображение в сообщении
    await message.answer_photo(photo, caption="Нейросеть: Kandinsky 2.2")
