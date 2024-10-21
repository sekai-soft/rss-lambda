# RSS-lambda
RSS-lambda is a webapp that performs operations on RSS feeds.

## Usage

### Web UI

There is a web UI available at [rss-lambda.xyz](https://rss-lambda.xyz)

From there, you can input what you want to do with the RSS feed,
and the webapp will generate a feed URL after your specified operation.

### Manual

You could also construct the after-operation feed URL manually.

You need to urlencode your feed url first.

For example, if your feed url is
```
https://nitter.example.net/twitter_handle/rss
```

You need to urlencode the url first, using tools like [urlencoder.org](https://www.urlencoder.org/)
```
https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss
```

### Filter a rss feed by including entries with certain keywords in their titles
Your filtered feed url will be this if you want to only include entries with `keyword1` and `keyword2` in their titles
```
https://rss-lambda.xyz/rss?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_title_incl_substrs&param=keyword1&param=keyword2
```

### Filter a rss feed by excluding entries with certain keywords in their titles
Your filtered feed url will be this if you want to exclude entries with `keyword1` and `keyword2` in their titles
```
https://rss-lambda.xyz/rss?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_title_excl_substrs&param=keyword1&param=keyword2
```

### Filter a rss feed by excluding entries with certain keywords in their descriptions
Your filtered feed url will be this if you want to exclude entries with `keyword1` and `keyword2` in their descriptions
```
https://rss-lambda.xyz/rss?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_desc_excl_substrs&param=keyword1&param=keyword2
```

### Filter a rss feed by only including entries with image(s) in their descriptions
Your filtered feed url will be this if you want to only include entries with image(s) in their descriptions
```
https://rss-lambda.xyz/rss?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_desc_cont_img
```

### (BETA) Filter a rss feed by only including entries with human image(s) in their descriptions
Your filtered feed url will be this if you want to only include entries with human image(s) in their descriptions
```
https://rss-lambda.xyz/rss_image_recog?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_desc_cont_img
```

### (BETA) Filter a rss feed by only including entries with dog image(s) in their descriptions
Your filtered feed url will be this if you want to only include entries with dog image(s) in their descriptions
```
https://rss-lambda.xyz/rss_image_recog?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_desc_cont_img_dog
```

### (BETA) Filter a rss feed by only including entries with cat image(s) in their descriptions
Your filtered feed url will be this if you want to only include entries with cat image(s) in their descriptions
```
https://rss-lambda.xyz/rss_image_recog?url=https%3A%2F%2Fnitter.example.net%2Ftwitter_handle%2Frss&op=filter_desc_cont_img_cat
```

## Self-hosting

You can use the following `docker-compose.yml` to run the program
```yaml
services:
  app:
    restart: always
    ports:
      - "5000:5000"
    image: ghcr.io/sekai-soft/rss-lambda:latest
```

The web UI will be exposed at port 5000

The image recognition endpoints are not enabled by default. In order to enable them, you need to

1. Download the model. Create a new directory `blobs` under the docker compose root directory, download and run the [`download.sh`](https://github.com/sekai-soft/rss-lambda/blob/master/blobs/download.sh) file under that `blobs` directory.

2. Use the following `docker-compose.yml` file instead to run the program
```yaml
services:
  app:
    restart: always
    ports:
      - "5000:5000"
    image: ghcr.io/sekai-soft/rss-lambda:latest
    volumes:
      - ./blobs:/app/blobs
      - ./cache:/app/cache
      - ./file_cache:/app/file_cache
```

TODO: `docker run -p 8501:8501 --mount type=bind,source=./blobs/yolov3,target=/models/yolov3 -e MODEL_NAME=yolov3 -t tensorflow/serving`

## Development

Open in VSCode, then run

```bash
pip install -r requirements.txt
flask run --reload
```

The webapp will be available at [localhost:5000](http://localhost:5000)

Run unit tests

```bash
python -m unittest discover
```
