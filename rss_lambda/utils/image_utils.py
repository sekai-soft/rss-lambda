import os
import os.path
import logging
import tempfile
import requests
from typing import Optional, Dict, List
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup

def is_cdata(s: str) -> bool:
    return s.startswith('<![CDATA[') and s.endswith(']]>')

def extract_images_from_description(e: etree.Element, root_nsmap: Dict) -> List[etree.Element]:
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

def download_image(src: str) -> Optional[str]:
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

def create_item_element_with_image(img_src: str, item_element_tag: str, original_link: Optional[str]=None) -> etree.Element:
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

def extract_link(e: etree.Element, root_nsmap: Dict) -> Optional[str]:
    link_e = e.find('link', root_nsmap)
    if link_e is None:
        return None
    return link_e.text