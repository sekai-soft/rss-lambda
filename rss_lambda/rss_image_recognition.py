from .process_rss_text import process_rss_text, ParsedRssText
from .lambdas import _extract_images_from_description
from .yolov3 import yolov3
from .abstract_expensive_rss_lambda import abstract_expensive_rss_lambda
from .rss_image_utils import _create_item_element_with_image, _extract_link

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
                if yolov3(img_src, 0.5, class_id):
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

def rss_image_recognition(rss_text: str, class_id: int, url: str) -> str:
    hash = url + ":" + str(class_id)
    
    return abstract_expensive_rss_lambda(
        rss_text,
        _image_recognition,
        hash,
        [class_id])
