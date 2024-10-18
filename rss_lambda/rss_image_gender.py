import logging
from PIL import Image
from .lambdas import _extract_images_from_description
from .process_rss_text import process_rss_text, ParsedRssText
from .abstract_expensive_rss_lambda import abstract_expensive_rss_lambda
from .rss_image_utils import _download_image, _create_item_element_with_image, _extract_link
from .llava import llava, LlavaResult

def _downsize_image(image_path: str):
    image = Image.open(image_path)
    image.thumbnail((100, 100))
    image.save(image_path)

def _image_gender(rss_text: str, male_or_female: bool) -> str:
    def processor(parsed_rss_text: ParsedRssText):
        root = parsed_rss_text.root
        parent = parsed_rss_text.parent
        items = parsed_rss_text.items

        matched_images = []
        for item in items:
            images = _extract_images_from_description(item, root.nsmap)
            for image in images:
                img_src = image.get('src')
                downloaded_image_path = _download_image(img_src)
                if downloaded_image_path is None:
                    logging.error(f"failed to download image from {image.get('src')}")
                    continue
                _downsize_image(downloaded_image_path)
                llava_result = llava(downloaded_image_path)
                if (male_or_female and llava_result == LlavaResult.MALE) \
                    or (not male_or_female and llava_result == LlavaResult.FEMALE):
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

def rss_image_gender(rss_text: str, male_or_female: bool, url: str) -> str:
    hash = "image-gender" + ":" + url + ":" + ("male" if male_or_female else "female")

    return abstract_expensive_rss_lambda(
        rss_text,
        _image_gender,
        hash,
        [male_or_female])