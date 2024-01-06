from typing import Optional
from lxml import etree
from lxml.etree import CDATA
from .rss_lambda import rss_lambda

def is_cdata(s: str) -> bool:
    return s.startswith('<![CDATA[') and s.endswith(']]>')

def _filter_by_description_excluding_substring(e: etree.Element, excluded_substring: str) -> Optional[etree.Element]:
    description_e = e.find('description')
    if description_e is None:
        return e
    description = description_e.text
    return e if excluded_substring not in description else None

def filter_by_description_excluding_substring(rss_url: str, excluded_substring: str) -> str:
    return rss_lambda(rss_url, lambda e: _filter_by_description_excluding_substring(e, excluded_substring))

def _filter_by_description_containing_image(e: etree.Element) -> Optional[etree.Element]:
    description_e = e.find('description')
    if description_e is None:
        return e
    try:
        cdata = etree.fromstring(description_e.text)
        return e if cdata.find('.//img') is not None else None
    except etree.ParseError:
        return e

def filter_by_description_containing_image(rss_url: str) -> str:
    return rss_lambda(rss_url, _filter_by_description_containing_image)
