# rss-lambda
Perform lambda on your rss feeds

## Usage
You need to urlencode your feed url first

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

## Self-host

You can use the following `docker-compose.yml` to run the program
```yaml
version: '3'
services:
  app:
    restart: always
    ports:
      - "5000:5000"
    image: ghcr.io/k-t-corp/rss-lambda:latest
```

The program will be exposed at port 5000 and you can then use a reverse proxy like Nginx to expose it to the Internet
