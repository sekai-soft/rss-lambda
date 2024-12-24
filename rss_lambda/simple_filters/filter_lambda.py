from typing import Callable, Optional, Dict
from lxml import etree
from ..utils.process_rss_text import ParsedRssText, process_rss_text

def filter_lambda(
        rss_text: str,
        rss_item_lambda: Callable[[etree.Element, Dict], Optional[etree.Element]]
) -> str:
    def processor(parsed_rss_text: ParsedRssText):
        root = parsed_rss_text.root
        parent = parsed_rss_text.parent
        items = parsed_rss_text.items

        # Filter the items or entries
        transformed_items = list(map(lambda item: rss_item_lambda(item, root.nsmap), items))

        # Remove all original items and appended kept items
        for item in items:
            parent.remove(item)
        for item in transformed_items:
            if item is not None:
                parent.append(item)

    return process_rss_text(rss_text, processor)
