# RSS-lambda

RSS-lambda transforms RSS feeds without RSS client lock-in

## Motivation

There are RSS clients that can perform transformations on RSS feeds, e.g. only keep entries with certain keywords, or translate texts of the entries

However, using those features from the RSS clients will create RSS client lock-in that prevents you from moving to another RSS client if you desire

RSS-lambda is an application that perform transformations on the server-side instead so that you can freely move to another RSS client while keeping the transformations. It's also self-hostable so that you don't even need to rely on the official server instance!

## Usage

There is an official server instance available at [rss-lambda.xyz](https://rss-lambda.xyz)

From the web UI, you can tell it what you want to do with the RSS feed, and it will generate a RSS feed URL after your specified transformation

Transformations include
* Filter a rss feed by including entries with certain keywords in their titles
* Filter a rss feed by excluding entries with certain keywords in their titles
* Filter a rss feed by including entries with certain keywords in their contents
* Filter a rss feed by excluding entries with certain keywords in their contents
* Filter a rss feed by only including entries with image(s) in their contents
* Merge with other feeds
* Convert a feed to an image only feed

## Self-hosting

You can use the following `docker-compose.yml` to self-host the application
```yaml
services:
  app:
    restart: always
    ports:
      - "5000:5000"
    image: ghcr.io/sekai-soft/rss-lambda:latest
```

The web UI will be exposed at port 5000

## Development

Open in VSCode, then run `flask run --reload`

The webapp will be available at [localhost:5000](http://localhost:5000)

Run unit tests `python -m unittest discover`
