from flask import Flask, request
from urllib.parse import unquote, urlparse
from rss_lambda.lambdas import filter_by_description_excluding_substrings, filter_by_description_containing_image
from rss_lambda.rss_lambda import RSSLambdaError

app = Flask(__name__)

@app.route("/")
def index():
    return "index"

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
    try:
        if op == "filter_desc_excl_substrs":
            if not params:
                return "No param provided", 400
            return filter_by_description_excluding_substrings(url, params)
        elif op == "filter_desc_cont_img":
            if params:
                return "No param expected", 400
            return filter_by_description_containing_image(url)
        else:
            return f"Unknown op {op}", 400
    except RSSLambdaError as e:
        return e.message, 500
