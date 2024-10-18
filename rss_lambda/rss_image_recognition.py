import os
import os.path
import logging
import tempfile
import requests
from typing import Optional, Dict
from urllib.parse import urlparse
from lxml import etree
from .process_rss_text import process_rss_text, ParsedRssText
from .lambdas import _extract_images_from_description
from .yolov3 import yolov3
from .abstract_expensive_rss_lambda import abstract_expensive_rss_lambda

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

def _create_item_element_with_image(img_src: str, item_element_tag: str, original_link: Optional[str]=None) -> etree.Element:
    item_element = etree.Element(item_element_tag)

    title_element = etree.Element('title')
    title_element.text = 'Image'
    item_element.append(title_element)

    description_element = etree.Element('description')
    description_element.text = etree.CDATA(f'<img src="{img_src}"></img>')
    item_element.append(description_element)

    guid_element = etree.Element('guid')
    guid_element.text = img_src
    item_element.append(guid_element)

    link_element = etree.Element('link')
    link_element.text = original_link if original_link else img_src
    item_element.append(link_element)

    return item_element

def _extract_link(e: etree.Element, root_nsmap: Dict) -> Optional[str]:
    link_e = e.find('link', root_nsmap)
    if link_e is None:
        return None
    return link_e.text

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
                    matched_images.append(_create_item_element_with_image(
                        img_src,
                        item.tag,
                        _extract_link(item, root.nsmap)))

        # remove all items and appended kept items
        for item in items:
            parent.remove(item)
        for item in matched_images:
            parent.append(item)

    return process_rss_text(rss_text, processor)

def rss_image_recognition(rss_text: str, class_id: int, url: str):
    hash = url + ":" + str(class_id)
    
    return abstract_expensive_rss_lambda(
        rss_text,
        _image_recognition,
        hash,
        [class_id])
