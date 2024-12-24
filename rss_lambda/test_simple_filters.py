import unittest
from typing import List
from .simple_filters.simple_filters import \
    filter_by_title_including_substrings,\
    filter_by_title_excluding_substrings,\
    filter_by_description_including_substrings,\
    filter_by_description_excluding_substrings,\
    filter_by_description_containing_image
from .test_utils import nitter_rss20_response


def _youtube_atom_response(titles: List[str]):
    def title_to_xml(title: str) -> str:
        return f"""<entry>
  <id>yt:video:bbbbbb</id>
  <yt:videoId>bbbbbb</yt:videoId>
  <yt:channelId>aaaaaa</yt:channelId>
  <title>{title}</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=bbbbbb"/>
  <author>
   <name>channel title</name>
   <uri>https://www.youtube.com/channel/aaaaaa</uri>
  </author>
  <published>{'2024-01-06T07:07:14+0000'}</published>
  <updated>{'2024-01-06T07:07:14+0000'}</updated>
  <media:group>
   <media:title>{title}</media:title>
   <media:content url="https://www.youtube.com/v/bbbbbb?version=3" type="application/x-shockwave-flash" width="640" height="390"/>
   <media:thumbnail url="https://i2.ytimg.com/vi/bbbbbb/hqdefault.jpg" width="480" height="360"/>
   <media:description>description</media:description>
   <media:community>
    <media:starRating count="114514" average="5.00" min="1" max="5"/>
    <media:statistics views="114514"/>
   </media:community>
  </media:group>
 </entry>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
 <link rel="self" href="http://www.youtube.com/feeds/videos.xml?channel_id=aaaaaa"/>
 <id>yt:channel:aaaaaa</id>
 <yt:channelId>aaaaaa</yt:channelId>
 <title>channel title</title>
 <link rel="alternate" href="https://www.youtube.com/channel/aaaaaa"/>
 <author>
  <name>channel title</name>
  <uri>https://www.youtube.com/channel/aaaaaa</uri>
 </author>
 <published>{'2024-01-06T07:07:14+0000'}</published>
 {'\n'.join(map(title_to_xml, titles))}
</feed>"""


class SimpleFiltersTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_filter_by_title_including_substrings(self):
        rss_text = _youtube_atom_response([
            'title 1',
            'title 2 but INCLUDE ME',
        ])
        self.assertEqual(
            filter_by_title_including_substrings(rss_text, ['INCLUDE ME']),
            _youtube_atom_response([
                'title 2 but INCLUDE ME',
            ])
        )

    def test_filter_by_title_excluding_substrings(self):
        rss_text = _youtube_atom_response([
            'title 1',
            'title 2 but EXCLUDE ME',
        ])
        self.assertEqual(
            filter_by_title_excluding_substrings(rss_text, ['EXCLUDE ME']),
            _youtube_atom_response([
                'title 1',
            ])
        )

    def test_filter_by_description_including_substrings(self):
        rss_text = nitter_rss20_response([
            '<p>some random text</p>',
            '<p>also some random texts but INCLUDE ME hahaha</p>',
        ])
        self.assertEqual(
            filter_by_description_including_substrings(rss_text, ['INCLUDE ME']),
            nitter_rss20_response([
                '<p>also some random texts but INCLUDE ME hahaha</p>',
            ])
        )

    def test_filter_by_description_excluding_substrings(self):
        rss_text = nitter_rss20_response([
            '<p>some random text</p>',
            '<p>also some random texts but EXCLUDE ME hahaha</p>',
        ])
        self.assertEqual(
            filter_by_description_excluding_substrings(rss_text, ['EXCLUDE ME']),
            nitter_rss20_response([
                '<p>some random text</p>',
            ])
        )

    def test_filter_by_description_containing_image(self):
        rss_text = nitter_rss20_response([
            '<p>some random text</p>',
            '<p>also some random texts</p><p>but without images haha</p>',
            '<p>also some random texts<br>but without images haha 2222</p> ',
            '<p>also some random texts but with images hahahaha</p><img src="https://nitter.example.com/twitter_handle/pic/pic.jpg" />',
        ])
        self.assertEqual(
            filter_by_description_containing_image(rss_text),
            nitter_rss20_response([
                '<p>also some random texts but with images hahahaha</p><img src="https://nitter.example.com/twitter_handle/pic/pic.jpg" />',
            ])
        )
