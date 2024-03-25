import os
import requests
import sentry_sdk
from typing import Union
from flask import Flask, request, Response, send_from_directory
from urllib.parse import unquote, urlparse
from rss_lambda.lambdas import \
    filter_by_title_including_substrings,\
    filter_by_title_excluding_substrings,\
    filter_by_description_excluding_substrings,\
    filter_by_description_containing_image
from rss_lambda.rss_lambda import RSSLambdaError


if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
    )


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


@app.route("/rss")
def rss():
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
