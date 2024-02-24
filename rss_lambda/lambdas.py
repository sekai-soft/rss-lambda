import logging
from typing import Optional, List, Dict
from lxml import etree
from bs4 import BeautifulSoup
from .rss_lambda import rss_lambda

def is_cdata(s: str) -> bool:
    return s.startswith('<![CDATA[') and s.endswith(']]>')

def _filter_by_title_including_substrings(e: etree.Element, root_nsmap: Dict, included_substrings: List[str]) -> Optional[etree.Element]:
    title_e = e.find('title', root_nsmap)
    if title_e is None:
        return e
    title = title_e.text
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

def _filter_by_description_containing_image(e: etree.Element, root_nsmap: Dict) -> Optional[etree.Element]:
    description_e = e.find('description', root_nsmap)
    if description_e is None:
        return e
    try:
        description_text = description_e.text
        if is_cdata(description_text):
            description_text = description_text[9:-3]
        soup = BeautifulSoup(description_text, 'html.parser')
        return None if soup.find('img') is None else e
    except Exception as ex:
        logging.error(f'_filter_by_description_containing_image failed to parse description text: {description_e.text}, error: {ex}')
        return e

def filter_by_description_containing_image(rss_text: str) -> str:
    return rss_lambda(rss_text, _filter_by_description_containing_image)
