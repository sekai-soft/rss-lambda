# RSS-lambda
RSS-lambda is a webapp that performs operations on RSS feeds.

## Usage

### Web UI

There is a web UI available at [rss-lambda.ktachibana.party](https://rss-lambda.ktachibana.party)

From there, you can input what you want to do with the RSS feed,
and the webapp will generate a feed URL after your specified operation.

### Manual

You could also construct the after-operation feed URL manually.

You need to urlencode your feed url first.

For example, if your feed url is
```
https://nitter.ktachibana.party/twitter_handle/rss
```

You need to urlencode the url first, using tools like [urlencoder.org](https://www.urlencoder.org/)
```
https%3A%2F%2Fnitter.ktachibana.party%2Ftwitter_handle%2Frss
```

### Filter a rss feed by including entries with certain keywords in their titles
Your filtered feed url will be this if you want to only include entries with `keyword1` and `keyword2` in their titles
```
https://rss-lambda.ktachibana.party/rss?url=https%3A%2F%2Fnitter.ktachibana.party%2Ftwitter_handle%2Frss&op=filter_title_incl_substrs&param=keyword1&param=keyword2
```

### Filter a rss feed by excluding entries with certain keywords in their titles
Your filtered feed url will be this if you want to exclude entries with `keyword1` and `keyword2` in their titles
```
https://rss-lambda.ktachibana.party/rss?url=https%3A%2F%2Fnitter.ktachibana.party%2Ftwitter_handle%2Frss&op=filter_title_excl_substrs&param=keyword1&param=keyword2
```

### Filter a rss feed by excluding entries with certain keywords in their descriptions
Your filtered feed url will be this if you want to exclude entries with `keyword1` and `keyword2` in their descriptions
```
https://rss-lambda.ktachibana.party/rss?url=https%3A%2F%2Fnitter.ktachibana.party%2Ftwitter_handle%2Frss&op=filter_desc_excl_substrs&param=keyword1&param=keyword2
```

### Filter a rss feed by only including entries with image(s) in their descriptions
Your filtered feed url will be this if you want to only include entries with image(s) in their descriptions
```
https://rss-lambda.ktachibana.party/rss?url=https%3A%2F%2Fnitter.ktachibana.party%2Ftwitter_handle%2Frss&op=filter_desc_cont_img
```

## Like what you see?
Consider support us on [Patreon](https://www.patreon.com/sekaisoft) :)

## Self-host

You can use the following `docker-compose.yml` to run the program
```yaml
version: '3'
services:
  app:
    restart: always
    ports:
      - "5000:5000"
    image: ghcr.io/sekai-soft/rss-lambda:latest
```

The program will be exposed at port 5000 and you can then use a reverse proxy like Nginx to expose it to the Internet

Optionally you can specify the port that the program listens to. This is useful in scenarios such as [setting up a Tailscale sidecar](https://tailscale.com/blog/docker-tailscale-guide?utm_source=pocket_reader) where you need to have the program listen to port 80
```yaml
version: '3'
services:
  app:
    restart: always
    image: ghcr.io/sekai-soft/rss-lambda:latest
    environment:
      - PORT=80
    # network_mode: service:tailscale-sidecar
```

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
