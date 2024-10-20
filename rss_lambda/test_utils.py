from typing import List


def nitter_rss20_response(description_htmls: List[str]):
    def description_html_to_xml(description_html: str) -> str:
        return f"""<item>
    <title>title</title>
    <dc:creator>@twitter_handle</dc:creator>
    <description><![CDATA[{description_html}]]></description>
    <pubDate>{"Sat, 06 Jan 2024 07:06:54 GMT"}</pubDate>
    <guid>http://nitter.example.com/twitter_handle/status/-1#m</guid>
    <link>http://nitter.example.com/twitter_handle/status/-1#m</link>
</item>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
  <channel>
    <atom:link href="http://nitter.example.com/twitter_handle/rss" rel="self" type="application/rss+xml"/>
    <title>twitter_handle / @twitter_handle</title>
    <link>http://nitter.example.com/twitter_handle</link>
    <description>Twitter feed for: @twitter_handle. Generated by nitter.example.com
</description>
    <language>en-us</language>
    <ttl>40</ttl>
    {'\n'.join(map(description_html_to_xml, description_htmls))}
</channel>
</rss>"""
