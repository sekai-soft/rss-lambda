import logging
import ollama
import base64
from multiprocessing import Process
from PIL import Image
from .rss_image_utils import _download_image

DOWNSIZE_SIZE = (50, 50)


def _downsize_image(image_path: str):
    image = Image.open(image_path)
    image = image.convert('RGB')
    image.thumbnail(DOWNSIZE_SIZE)
    image.save(image_path)


LLAVA_MODEL_NAME = 'llava:latest'


def is_llava_available():
    models = ollama.list()['models']
    for model in models:
        if model['name'] == LLAVA_MODEL_NAME:
            return True

    logging.info(f"pulling model {LLAVA_MODEL_NAME}")

    def _pull_model():
        ollama.pull(LLAVA_MODEL_NAME)
    Process(target=_pull_model).start()

    return False


LLAVA_RESULT_NO = "no"
LLAVA_RESULT_MALE = "male"
LLAVA_RESULT_FEMALE = "female"
LLAVA_RESULT_ERROR = "error"


PROMPT = """
Is there a human in this image? If yes, do they show male or female characteristics?
Return only one of those three strings: "no", "male" or "female".
"""


def llava(image_url: str) -> str:
    image_path = _download_image(image_url)
    if image_path is None:
        logging.error(f"failed to download image from {image_url}")
        return LLAVA_RESULT_ERROR
    _downsize_image(image_path)

    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())

    response = ollama.generate(
        model=LLAVA_MODEL_NAME,
        prompt=PROMPT,
        images=[encoded_image])
    response = response['response']
    response = response.lower()

    if "female" in response:
        return LLAVA_RESULT_FEMALE
    elif "male" in response:
        return LLAVA_RESULT_MALE
    elif "no" in response:
        return LLAVA_RESULT_NO
    logging.error(f"llava failed to process image {image_path}, response was: {response}")
    return LLAVA_RESULT_ERROR
