from typing import Optional, List, Dict
from lxml import etree
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
        # wrap description text in a placeholder <description> tag to parse it as a valid XML document
        # in case the text within contains multiple root elements, e.g. <p>text1</p><p>text2</p>
        # and thus failing to parse and mistakenly returns it as a valid entry because of etree.ParseError
        cdata = etree.fromstring("<description>"+description_e.text+"</description>")
        return e if cdata.find('.//img') is not None else None
    except etree.ParseError:
        return e

def filter_by_description_containing_image(rss_text: str) -> str:
    return rss_lambda(rss_text, _filter_by_description_containing_image)
