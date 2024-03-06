# Example posting a image URL:

import requests
r = requests.post(
    "https://api.deepai.org/api/image-editor",
    data={
        'image': 'YOUR_IMAGE_URL',
        'text': 'YOUR_IMAGE_URL',
    },
    headers={'api-key': 'f3233110-f510-4127-b02e-07256bfa3459'}
)
print(r.json())


# Example posting a local image file:

import requests
r = requests.post(
    "https://api.deepai.org/api/image-editor",
    files={
        'image': open('/path/to/your/file.jpg', 'rb'),
        'text': open('/path/to/your/file.txt', 'rb'),
    },
    headers={'api-key': 'f3233110-f510-4127-b02e-07256bfa3459'}
)
print(r.json())