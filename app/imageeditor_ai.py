import requests
import time
import shutil
import json

headers = {"Authorization": "e021111e1ad1438bae20c3a5eff3b35a"}
params = {
    "terms": "Миска котят",
    "is_sfw": True,
    "replacing": "фрукты и плодоножки",
    "negative_terms": "",
    "fix_faces": True,
    "outpaint": False,
    "upscale": False,
}
file_path = "path/to/test.jpeg"
base_api_url = "https://api.imageeditor.ai"
api_url = f"{base_api_url}/v1"


def download_file(url, local_filename):
    url = f"{base_api_url}/{url}"
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename


def convert_files(api_url, params, headers):
    files = [eval(f'("files", open("{file_path}", "rb"))')]
    r = requests.post(
        url=f"{api_url}/edit-image/",
        files=files,
        data=params,
        headers=headers
    )
    return r.json()


def get_results(params):
    if params.get("error"):
        print(params)
        return

    r = requests.post(
        url=f"{api_url}/results/",
        data=params
    )
    data = r.json()
    finished = data.get("finished")

    while not finished:
        if int(data.get("queue_count")) > 0:
            print("queue: %s" % data.get("queue_count"))

        time.sleep(5)
        results = get_results(params)
        results = json.dumps(results)

        if results:
            break

    if finished:
        for f in data.get("files"):
            print(f.get("url"))
            download_file("%s" % f.get("url"), "%s" % f.get("filename"))
        return {"finished": "files downloaded"}
    return r.json()


get_results(convert_files(api_url, params, headers))
