from typing import Optional, List, Dict, Callable
from lxml import etree
from .filter_lambda import filter_lambda
from ..utils.image_utils import extract_images_from_description

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
    return filter_lambda(rss_text, lambda e, root_nsmap: _filter_by_title_including_substrings(e, root_nsmap, included_substrings))

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
    return filter_lambda(rss_text, lambda e, root_nsmap: _filter_by_title_excluding_substrings(e, root_nsmap, excluded_substrings))

def _filter_by_description_including_substrings(e: etree.Element, root_nsmap: Dict, included_substrings: List[str]) -> Optional[etree.Element]:
    description_e = e.find('description', root_nsmap)

    media_description_e = None
    if 'media' in root_nsmap:
        media_group_e = e.find('media:group', root_nsmap)
        if media_group_e is not None:
            media_description_e = media_group_e.find('media:description', root_nsmap)

    description = None
    if media_description_e is not None:
        description = media_description_e.text
    elif description_e is not None:
        description = description_e.text

    if description is None:
        return e
    for substr in included_substrings:
        if substr in description:
            return e
    return None

def filter_by_description_including_substrings(rss_text: str, included_substrings: List[str]) -> str:
    return filter_lambda(rss_text, lambda e, root_nsmap: _filter_by_description_including_substrings(e, root_nsmap, included_substrings))

def _filter_by_description_excluding_substrings(e: etree.Element, root_nsmap: Dict, excluded_substrings: List[str]) -> Optional[etree.Element]:
    description_e = e.find('description', root_nsmap)

    media_description_e = None
    if 'media' in root_nsmap:
        media_group_e = e.find('media:group', root_nsmap)
        if media_group_e is not None:
            media_description_e = media_group_e.find('media:description', root_nsmap)

    description = None
    if media_description_e is not None:
        description = media_description_e.text
    elif description_e is not None:
        description = description_e.text

    if description is None:
        return e
    for substr in excluded_substrings:
        if substr in description:
            return None
    return e

def filter_by_description_excluding_substrings(rss_text: str, excluded_substrings: List[str]) -> str:
    return filter_lambda(rss_text, lambda e, root_nsmap: _filter_by_description_excluding_substrings(e, root_nsmap, excluded_substrings))

def _filter_by_description_containing_image(e: etree.Element, root_nsmap: Dict) -> Optional[etree.Element]:
    images = extract_images_from_description(e, root_nsmap)
    if len(images) == 0:
        return None
    return e

def filter_by_description_containing_image(rss_text: str) -> str:
    return filter_lambda(rss_text, _filter_by_description_containing_image)
