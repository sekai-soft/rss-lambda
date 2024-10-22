import os
import logging
import time
import requests
import json
from .rss_image_utils import _download_image
from .file_cache import file_cache

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

tfserving_root = os.getenv("TFSERVING_ROOT", "http://localhost:8501")
size = 320


@file_cache(verbose=True)
def yolov3_tf(image_url: str, desired_class_id: int) -> bool:
    start_time = time.time()

    # Downlaod image
    image_path = _download_image(image_url)
    if image_path is None:
        logging.error(f"failed to download image from {image.get('src')}")
        return False

    # Decode image
    image = tf.image.decode_image(open(image_path, 'rb').read(), channels=3)
    image = tf.expand_dims(image, axis=0)
    image = tf.image.resize(image, (size, size))
    image = image / 255
    
    # Make request
    data = {
        "signature_name": "serving_default",
        "instances": image.numpy().tolist()
    }
    resp = requests.post(f"{tfserving_root}/v1/models/yolov3:predict", json=data)
    resp = json.loads(resp.content.decode('utf-8'))['predictions'][0]

    res = False
    valid_predictions = resp['yolo_nms_3']
    for i in range(valid_predictions):
        clazz = resp['yolo_nms_2'][i]
        if clazz == desired_class_id:
            res = True
            break

    logging.info(f"yolov3 tf took {time.time() - start_time} seconds")

    return res
