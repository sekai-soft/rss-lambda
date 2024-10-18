import feedparser
from typing import List, Callable
from dataclasses import dataclass
from lxml import etree
from .rss_lambda_error import RSSLambdaError

supported_feed_versions = ["rss20", "atom10", "atom03"]
xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'


@dataclass
class ParsedRssText:
    root: etree.Element
    parent: etree.Element
    items: List[etree.Element]

def process_rss_text(rss_text: str, processor: Callable[[ParsedRssText], None]) -> str:
    # Determine if it's a valid and supported feed
    feed = feedparser.parse(rss_text)
    if feed.bozo != 0:
        raise RSSLambdaError(f"Failed to parse the feed")
    if feed.version not in supported_feed_versions:
        raise RSSLambdaError(f"Unsupported feed version: {feed.version}")

    # Parse the feed and find the parent element of the items or entries
    lxml_parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(rss_text.encode('utf-8'), parser=lxml_parser)
    if feed.version == 'rss20':
        parent = root.find('./channel')
        items = parent.findall('item')
    elif feed.version in ['atom10', 'atom03']:
        parent = root
        items = parent.findall('{http://www.w3.org/2005/Atom}entry')
    else:
        raise RSSLambdaError(f"Escaped unsupported feed version: {feed.version}")
    
    processor(ParsedRssText(
        root=root,
        parent=parent,
        items=items))

    # Return processed feed
    if xml_declaration in rss_text:
        return xml_declaration + '\n' + etree.tostring(root, encoding='unicode')
    else:
        return etree.tostring(root, encoding='unicode')
