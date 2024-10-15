import os
import os.path
import logging
import tempfile
import hashlib
import requests
from typing import Optional
from multiprocessing import Process
from urllib.parse import urlparse
from lxml import etree
from .process_rss_text import process_rss_text, ParsedRssText
from .lambdas import _extract_images_from_description
from .yolov3 import yolov3


_cache_root_path = os.path.join('cache')
if not os.path.exists(_cache_root_path):
    os.mkdir(_cache_root_path)

def _get_cache_path(hash_key: str, suffix: str) -> str:
    return os.path.join(_cache_root_path, f"{hash_key}-{suffix}")

def _cache_exists(hash_key: str, suffix: str) -> bool:
    return os.path.isfile(_get_cache_path(hash_key, suffix))

def _write_cache(hash_key: str, suffix: str, content: str):
    with open(_get_cache_path(hash_key, suffix), 'w') as f:
        f.write(content)

def _read_cache(hash_key: str, suffix: str) -> str:
    with open(_get_cache_path(hash_key, suffix)) as f:
        return f.read()

def _empty_list(rss_text: str) -> str:
    def processor(parsed_rss_text: ParsedRssText):
        parent = parsed_rss_text.parent
        items = parsed_rss_text.items
    
        # remove all items
        for item in items:
            parent.remove(item)

    return process_rss_text(rss_text, processor)

def _download_image(src: str) -> Optional[str]:
    # Parse the URL to get the file extension
    parsed_url = urlparse(src)
    file_extension = os.path.splitext(parsed_url.path)[1]
    if not file_extension:
        file_extension = '.jpg'

    # Create a temporary file with the correct extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        # Download the image
        response = requests.get(src)
        if response.status_code == 200:
            temp_file.write(response.content)
            return temp_file.name
        else:
            logging.error(f"failed to download image from {src}: HTTP status {response.status_code}")
            return None

def _create_item_element_with_image(img_src: str, item_element_tag: str) -> etree.Element:
    item_element = etree.Element(item_element_tag)

    title_element = etree.Element('title')
    title_element.text = 'Image'
    item_element.append(title_element)

    description_element = etree.Element('description')
    description_element.text = etree.CDATA(f'<img src="{img_src}"></img>')
    item_element.append(description_element)

    return item_element

def _image_recognition(rss_text: str, class_id: int) -> str:
    def processor(parsed_rss_text: ParsedRssText):
        root = parsed_rss_text.root
        parent = parsed_rss_text.parent
        items = parsed_rss_text.items

        matched_images = []
        for item in items:
            images = _extract_images_from_description(item, root.nsmap)
            for image in images:
                img_src = image.get('src')
                downloaded_image_path = _download_image(img_src)
                if downloaded_image_path is None:
                    logging.error(f"failed to download image from {image.get('src')}")
                    continue
                if yolov3(downloaded_image_path, 0.5, class_id):
                    matched_images.append(_create_item_element_with_image(img_src, item.tag))

        # remove all items and appended kept items
        for item in items:
            parent.remove(item)
        for item in matched_images:
            parent.append(item)

    return process_rss_text(rss_text, processor)


ORIGINAL_CACHE_SUFFIX = 'original'
PROCESSED_CACHE_SUFFIX = 'processed'

def rss_image_recognition(rss_text: str, class_id: int, url: str):
    # obtain hash key
    hashed_text = url + ":" + str(class_id)
    h = hashlib.new('sha256')
    h.update(hashed_text.encode())
    hash_key = h.hexdigest()

    if not _cache_exists(hash_key, ORIGINAL_CACHE_SUFFIX):
        # original cache does not exist, process and cache original and processed
        logging.info(f"original cache does not exist for {hashed_text}, processing")
        _write_cache(hash_key, ORIGINAL_CACHE_SUFFIX, rss_text)

        def _process():
            processed_rss_text = _image_recognition(rss_text, class_id)
            _write_cache(hash_key, PROCESSED_CACHE_SUFFIX, processed_rss_text)
            logging.info(f"processed and cached {hashed_text}")
        Process(target=_process).start()

        return _empty_list(rss_text)

    if not _cache_exists(hash_key, PROCESSED_CACHE_SUFFIX):
        # original cache exists but processed cache does not exist, 
        # it is being processed, return empty list
        logging.info(f"processed cache does not exist for {hashed_text}. it is still processing")
        return _empty_list(rss_text)

    processed_cache = _read_cache(hash_key, PROCESSED_CACHE_SUFFIX)
    if _read_cache(hash_key, ORIGINAL_CACHE_SUFFIX) == rss_text:
        # original cache exists and was not updated, return processed cache
        logging.info(f"original cache exists for {hashed_text} and was not updated, returning processed cache")
        return processed_cache

    # original cache exists but was updated,
    # process and cache updated original and updated processed
    logging.info(f"original cache exists for {hashed_text} but was updated, processing")
    def _process():
        processed_rss_text = _image_recognition(rss_text, class_id)
        _write_cache(hash_key, ORIGINAL_CACHE_SUFFIX, rss_text)
        _write_cache(hash_key, PROCESSED_CACHE_SUFFIX, processed_rss_text)
        logging.info(f"processed and cached {hashed_text}")
    Process(target=_process).start()

    return processed_cache
