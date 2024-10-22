import os
import os.path
import logging
import hashlib
import datetime
from typing import Any, List
from multiprocessing import Process
from lxml import etree
from .process_rss_text import process_rss_text, ParsedRssText

stale_cache_threshold_seconds = 5 * 60  # 5 minutes

_cache_root_path = os.path.join('cache')
os.makedirs(_cache_root_path, exist_ok=True)

def _get_cache_path(hash_key: str, suffix: str) -> str:
    return os.path.join(_cache_root_path, f"{hash_key}-{suffix}")

def _cache_exists(hash_key: str, suffix: str) -> bool:
    return os.path.isfile(_get_cache_path(hash_key, suffix))

def _write_cache(hash_key: str, suffix: str, content: str):
    with open(_get_cache_path(hash_key, suffix), 'w') as f:
        f.write(content)

def _read_cache(hash_key: str, suffix: str) -> str:
    with open(_get_cache_path(hash_key, suffix)) as f:
        return f.read()

def _remove_cache(hash_key: str, suffix: str):
    os.remove(_get_cache_path(hash_key, suffix))

def _cache_is_stale(hash_key: str, suffix: str) -> bool:
    creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(_get_cache_path(hash_key, suffix)))
    return (datetime.datetime.now() - creation_time).total_seconds() > stale_cache_threshold_seconds

def _empty_list(rss_text: str) -> str:
    def processor(parsed_rss_text: ParsedRssText):
        parent = parsed_rss_text.parent
        items = parsed_rss_text.items

        # remove all items
        for item in items:
            parent.remove(item)

        # add item for notice
        if items:
            notice_item_element = etree.Element(items[0].tag)

            title_element = etree.Element('title')
            title_element.text = 'Processing, please refresh later...'
            notice_item_element.append(title_element)

            guid_element = etree.Element('guid')
            guid_element.text = "Processing, please refresh later..."
            notice_item_element.append(guid_element)

            parent.append(notice_item_element)

    return process_rss_text(rss_text, processor)

ORIGINAL_CACHE_SUFFIX = 'original'
PROCESSED_CACHE_SUFFIX = 'processed'
PROCESSING_LOCK_CACHE_SUFFIX = 'processing-lock'

def abstract_expensive_rss_lambda(rss_text: str, expensive_operation, hash: str, extra_args: List[Any]) -> str:
    # obtain hash keY
    h = hashlib.new('sha256')
    h.update(hash.encode())
    hash_key = h.hexdigest()

    if not _cache_exists(hash_key, ORIGINAL_CACHE_SUFFIX):
        # original cache does not exist, start processing (use absence of processed cache as lock)
        logging.info(f"(first processing) original cache does not exist for {hash}, start processing")
        _write_cache(hash_key, ORIGINAL_CACHE_SUFFIX, rss_text)

        def _process():
            processed_rss_text = expensive_operation(rss_text, *extra_args)
            _write_cache(hash_key, PROCESSED_CACHE_SUFFIX, processed_rss_text)
            logging.info(f"(first processing) processed and cached {hash}")
        Process(target=_process).start()

        return _empty_list(rss_text)

    if not _cache_exists(hash_key, PROCESSED_CACHE_SUFFIX):
        if _cache_is_stale(hash_key, ORIGINAL_CACHE_SUFFIX):
            # original cache is stale, remove and reprocess
            logging.info(f"(first processing) original cache is stale for {hash}, removing")
            _remove_cache(hash_key, ORIGINAL_CACHE_SUFFIX)
            return _empty_list(rss_text)

        # original cache exists but processed cache does not exist. it is being processed, return empty list.
        logging.info(f"(first processing) processed cache does not exist for {hash} so it's still processing")
        return _empty_list(rss_text)

    processed_cache = _read_cache(hash_key, PROCESSED_CACHE_SUFFIX)
    if _read_cache(hash_key, ORIGINAL_CACHE_SUFFIX) == rss_text:
        # original cache exists and was not updated, return processed cache
        logging.info(f"original cache exists for {hash} and was not updated, returning processed cache")
        return processed_cache

    if _cache_exists(hash_key, PROCESSING_LOCK_CACHE_SUFFIX):
        if _cache_is_stale(hash_key, PROCESSING_LOCK_CACHE_SUFFIX):
            # original cache exists but was updated and processing lock is stale, remove and reprocess
            logging.info(f"original cache exists for {hash} but was updated and processing lock is stale, removing")
            _remove_cache(hash_key, PROCESSING_LOCK_CACHE_SUFFIX)
            return _empty_list(rss_text)

        # original cache exists but was updated and is still processing, return processed cache
        logging.info(f"original cache exists for {hash} but was updated and is still processing")
        return processed_cache

    # original cache exists but was updated and hasn't been processed yet, start processing and return processed cache
    logging.info(f"original cache exists for {hash} but was updated, start processing")
    _write_cache(hash_key, PROCESSING_LOCK_CACHE_SUFFIX, 'locked')
    def _process():
        processed_rss_text = expensive_operation(rss_text, *extra_args)
        _write_cache(hash_key, ORIGINAL_CACHE_SUFFIX, rss_text)
        _write_cache(hash_key, PROCESSED_CACHE_SUFFIX, processed_rss_text)
        _remove_cache(hash_key, PROCESSING_LOCK_CACHE_SUFFIX)
        logging.info(f"processed and cached {hash}")
    Process(target=_process).start()

    return processed_cache
