import enum
import logging
import ollama
import base64
from multiprocessing import Process


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


class LlavaResult(enum.Enum):
    NO = "no"
    MALE = "male"
    FEMALE = "female"
    ERROR = "error"


PROMPT = """
Is there a human in this image? If yes, do they show male or female characteristics?
Return only one of those three strings: "no", "male" or "female".
"""


def llava(image_path: str) -> LlavaResult:
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())

    response = ollama.generate(
        model=LLAVA_MODEL_NAME,
        prompt=PROMPT,
        images=[encoded_image])
    response = response['response']
    response = response.lower()

    if "female" in response:
        return LlavaResult.FEMALE
    elif "male" in response:
        return LlavaResult.MALE
    elif "no" in response:
        return LlavaResult.NO
    logging.error(f"llava failed to process image {image_path}, response was: {response}")
    return LlavaResult.ERROR
