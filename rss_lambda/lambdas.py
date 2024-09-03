import logging
import tempfile
import os
import requests
from typing import Optional, List, Dict
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
from .rss_lambda import rss_lambda
from .yolov3 import is_yolov3_available, yolov3

def is_cdata(s: str) -> bool:
    return s.startswith('<![CDATA[') and s.endswith(']]>')

def _filter_by_title_including_substrings(e: etree.Element, root_nsmap: Dict, included_substrings: List[str]) -> Optional[etree.Element]:
    title_e = e.find('title', root_nsmap)
    if title_e is None:
        return e
    title = title_e.text
    if title is None:
        return e
    for substr in included_substrings:
        if substr in title:
            return e
    return None

def filter_by_title_including_substrings(rss_text: str, included_substrings: List[str]) -> str:
    return rss_lambda(rss_text, lambda e, root_nsmap: _filter_by_title_including_substrings(e, root_nsmap, included_substrings))

def _filter_by_title_excluding_substrings(e: etree.Element, root_nsmap: Dict, excluded_substrings: List[str]) -> Optional[etree.Element]:
    title_e = e.find('title', root_nsmap)
    if title_e is None:
        return e
    title = title_e.text
    if title is None:
        return e
    for substr in excluded_substrings:
        if substr in title:
            return None
    return e

def filter_by_title_excluding_substrings(rss_text: str, excluded_substrings: List[str]) -> str:
    return rss_lambda(rss_text, lambda e, root_nsmap: _filter_by_title_excluding_substrings(e, root_nsmap, excluded_substrings))

def _filter_by_description_excluding_substrings(e: etree.Element, root_nsmap: Dict, excluded_substrings: List[str]) -> Optional[etree.Element]:
    description_e = e.find('description', root_nsmap)
    if description_e is None:
        return e
    description = description_e.text
    for substr in excluded_substrings:
        if substr in description:
            return None
    return e

def filter_by_description_excluding_substrings(rss_text: str, excluded_substrings: List[str]) -> str:
    return rss_lambda(rss_text, lambda e, root_nsmap: _filter_by_description_excluding_substrings(e, root_nsmap, excluded_substrings))

def _extract_images_from_description(e: etree.Element, root_nsmap: Dict) -> List[etree.Element]:
    description_e = e.find('description', root_nsmap)
    if description_e is None:
        return []
    try:
        description_text = description_e.text
        if is_cdata(description_text):
            description_text = description_text[9:-3]
        soup = BeautifulSoup(description_text, 'html.parser')
        return soup.find_all('img')
    except Exception as ex:
        logging.error(f'failed to parse description text: {description_e.text}, error: {ex}')
        return []

def _filter_by_description_containing_image(e: etree.Element, root_nsmap: Dict) -> Optional[etree.Element]:
    images = _extract_images_from_description(e, root_nsmap)
    if len(images) == 0:
        return None
    return e

def filter_by_description_containing_image(rss_text: str) -> str:
    return rss_lambda(rss_text, _filter_by_description_containing_image)

def filter_by_description_containing_image_human(rss_text: str) -> str:
    return rss_lambda(rss_text, _filter_by_description_containing_image_human)

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

def _filter_by_description_containing_image_human(e: etree.Element, root_nsmap: Dict) -> Optional[etree.Element]:
    if not is_yolov3_available():
        logging.error("yolov3 is not available")
        return None
    images = _extract_images_from_description(e, root_nsmap)
    if len(images) == 0:
        return None
    for image in images:
        downloaded_image_path = _download_image(image.get('src'))
        if downloaded_image_path is None:
            logging.error(f"failed to download image from {image.get('src')}")
            continue
        if yolov3(downloaded_image_path, 0.5, 0):
            return e
    return None
