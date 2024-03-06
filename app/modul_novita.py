import requests


async def novita_img2img(message, image):
    response = requests.get(
        'https://www.cutout.pro/api/v1/faceDriven/submitTaskByUrl?imageUrl=xxxx&templateId=1',
        headers={'APIKEY': '307cc03cc3ab4cc38c078ac29bacfbaf'},
    )
