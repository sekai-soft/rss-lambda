import os
import requests
import sentry_sdk
from typing import Union
from flask import Flask, request, Response, send_from_directory, send_file
from urllib.parse import unquote, urlparse
from rss_lambda.lambdas import \
    filter_by_title_including_substrings,\
    filter_by_title_excluding_substrings,\
    filter_by_description_including_substrings,\
    filter_by_description_excluding_substrings,\
    filter_by_description_containing_image
from rss_lambda.rss_lambda_error import RSSLambdaError
from rss_lambda.llava import is_llava_available
from rss_lambda.rss_image_gender import rss_image_gender
from rss_lambda.rss_image_recognition_tf import rss_image_recognition_tf
from rss_lambda.rss_merger import rss_merger


if os.getenv('SENTRY_DSN'):
    print("Sentry enabled")
    sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
else:
    print("Sentry disabled")


max_params = 50

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')


def download_feed(rss_url: str, headers) -> Union[str, Response]:
    try:
        res = requests.get(rss_url, headers={
            'User-Agent': headers.get('User-Agent', '')
        })
        if res.status_code >= 400 and res.status_code < 600:
            return Response(res.content, res.status_code)
        return res.text
    except Exception as _:
        return Response("Failed to download the feed", 500)


@app.route("/rss_image_recog")
def _rss_image_recog():
    # parse url
    url = request.args.get('url', default=None)
    if not url:
        return "No url provided", 400
    url = unquote(url)
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return "Invalid url", 400
    rss_text_or_res = download_feed(url, request.headers)
    if not isinstance(rss_text_or_res, str):
        return rss_text_or_res

    # parse class_id
    class_id = request.args.get('class_id', default=None)
    if not class_id:
        return "No class_id provided", 400
    
    # Hack for Reeder (iOS)
    if class_id.endswith("/rss"):
        class_id = class_id[:-4]
    if class_id.endswith("/feed"):
        class_id = class_id[:-5]

    class_id = int(class_id)

    try:
        return Response(rss_image_recognition_tf(rss_text_or_res, class_id, url), mimetype='application/xml')
    except RSSLambdaError as e:
        return e.message, 500


@app.route("/rss_image_gender")
def _rss_image_gender():
    if not is_llava_available():
        return "Image render is not enabled", 400

    # parse url
    url = request.args.get('url', default=None)
    if not url:
        return "No url provided", 400
    url = unquote(url)
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return "Invalid url", 400
    rss_text_or_res = download_feed(url, request.headers)
    if not isinstance(rss_text_or_res, str):
        return rss_text_or_res

    # parse gender
    gender = request.args.get('gender', default=None)
    if not gender:
        return "No gender provided", 400
    
    # Hack for Reeder (iOS)
    if gender.endswith("/rss"):
        gender = gender[:-4]
    if gender.endswith("/feed"):
        gender = gender[:-5]

    gender = gender == '1'

    try:
        return Response(rss_image_gender(rss_text_or_res, gender, url), mimetype='application/xml')
    except RSSLambdaError as e:
        return e.message, 500
    

@app.route("/rss")
def _rss():
    # parse url
    url = request.args.get('url', default=None)
    if not url:
        return "No url provided", 400
    url = unquote(url)
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return "Invalid url", 400
    
    # parse op
    op = request.args.get('op', default=None)
    if not op:
        return "No op provided", 400

    params = request.args.getlist('param')
    if len(params) > max_params:
        return f"Too many params, max {max_params} params allowed", 400
    try:
        if op == "filter_title_incl_substrs":
            if not params:
                return "No param provided", 400
            rss_text_or_res = download_feed(url, request.headers)
            if isinstance(rss_text_or_res, str):
                return Response(filter_by_title_including_substrings(rss_text_or_res, params), mimetype='application/xml')
            return rss_text_or_res
        elif op == "filter_title_excl_substrs":
            if not params:
                return "No param provided", 400
            rss_text_or_res = download_feed(url, request.headers)
            if isinstance(rss_text_or_res, str):
                return Response(filter_by_title_excluding_substrings(rss_text_or_res, params), mimetype='application/xml')
            return rss_text_or_res
        elif op == "filter_desc_incl_substrs":
            if not params:
                return "No param provided", 400
            rss_text_or_res = download_feed(url, request.headers)
            if isinstance(rss_text_or_res, str):
                return Response(filter_by_description_including_substrings(rss_text_or_res, params), mimetype='application/xml')
            return rss_text_or_res
        elif op == "filter_desc_excl_substrs":
            if not params:
                return "No param provided", 400
            rss_text_or_res = download_feed(url, request.headers)
            if isinstance(rss_text_or_res, str):
                return Response(filter_by_description_excluding_substrings(rss_text_or_res, params), mimetype='application/xml')
            return rss_text_or_res
        elif op == "filter_desc_cont_img":
            if params:
                return "No param expected", 400
            rss_text_or_res = download_feed(url, request.headers)
            if isinstance(rss_text_or_res, str):
                return Response(filter_by_description_containing_image(rss_text_or_res), mimetype='application/xml')
            return rss_text_or_res
        else:
            return f"Unknown op {op}", 400
    except RSSLambdaError as e:
        return e.message, 500


@app.route("/rss_merger")
def _rss_merger():
    # parse urls
    urls = request.args.getlist('url')
    if not urls:
        return "No url provided", 400
    if len(urls) == 1:
        return "At least two urls are required", 400
    urls = [unquote(url) for url in urls]
    for url in urls:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return "Invalid url", 400

    rss_texts = [download_feed(url, request.headers) for url in urls]
    for rss_text_or_res in rss_texts:
        if not isinstance(rss_text_or_res, str):
            return rss_text_or_res

    try:
        return Response(rss_merger(rss_texts), mimetype='application/xml')
    except RSSLambdaError as e:
        return e.message, 500


@app.route("/test_rss")
def _test_rss():
    return send_file('test-rss.xml', 'application/xml')
