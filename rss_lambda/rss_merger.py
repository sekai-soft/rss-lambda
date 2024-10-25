from typing import List, Optional
from .process_rss_text import parse_rss_text, wrap_items_to_rss_text


def get_guid(item) -> Optional[str]:
    guid_e = item.find('guid')
    if guid_e is not None:
        return guid_e.text
    return None


def rss_merger(rss_texts: List[str]) -> str:
    parsed_rss_texts = list(map(parse_rss_text, rss_texts))

    final_items = []
    appeared_guids = set()
    for parsed_rss_text in parsed_rss_texts:
        for item in parsed_rss_text.items:
            guid = get_guid(item)
            if guid is None:
                final_items.append(item)
            elif guid not in appeared_guids:
                final_items.append(item)
                appeared_guids.add(guid)

    first_parsed_rss_text = parsed_rss_texts[0]
    for item in first_parsed_rss_text.items:
        first_parsed_rss_text.parent.remove(item)
    for item in final_items:
        first_parsed_rss_text.parent.append(item)

    return wrap_items_to_rss_text(rss_texts[0], first_parsed_rss_text)
