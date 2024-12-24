import copy
from lxml import etree
from ..utils.process_rss_text import ParsedRssText, process_rss_text
from ..utils.image_utils import extract_images_from_description

MAX_IMAGES_PER_ITEM = 4

def to_image_feed(rss_text: str) -> str:
    def processor(parsed_rss_text: ParsedRssText):
        root = parsed_rss_text.root
        parent = parsed_rss_text.parent
        items = parsed_rss_text.items

        def handle_image(item, image):
            image_link = image.get('src')

            new_item = copy.deepcopy(item)
            new_description = new_item.find('description', root.nsmap)
            new_description.text = etree.CDATA(f'<img src="{image_link}"></img>')

            parent.append(new_item)

        def handle_item(item):
            description_e = item.find('description', root.nsmap)
            if description_e is None:
                return
            description = description_e.text
            if description is None:
                return
            images = extract_images_from_description(item, root.nsmap)
            if not images:
                return
            for image in images[: MAX_IMAGES_PER_ITEM]:
                handle_image(item, image)

        for item in items:
            handle_item(item)
            parent.remove(item)

    return process_rss_text(rss_text, processor)
