import enum
import logging
import ollama
import base64
import json
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
Return only in valid JSON string with one JSON key "result" and value being either "no", "male" or "female".
"""


def llava(image_path: str) -> LlavaResult:
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())

    response = ollama.generate(
        model=LLAVA_MODEL_NAME,
        prompt=PROMPT,
        images=[encoded_image])
    response = response['response']

    # response might still return markdown wrapper so sanitize it
    response = response.replace('```markdown', '').replace('```', '').strip()
    try:
        response = json.loads(response)
        return LlavaResult(response['result'])
    except Exception as e:
        logging.error(f"error parsing response: {response}, {e}")
        return LlavaResult.ERROR
