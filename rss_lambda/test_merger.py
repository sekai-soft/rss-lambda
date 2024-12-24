import unittest
from typing import List, Tuple
from .merger.merger import merger


def _nyt_rss_response(guid_and_pub_dates: List[Tuple[str, str]]):
    def guid_and_pub_date_to_xml(guid_and_pub_date: Tuple[str, str]) -> str:
        guid, pub_date = guid_and_pub_date[0], guid_and_pub_date[1]
        return f"""<item>
  <title>{guid}</title>
  <guid isPermaLink="true">{guid}</guid>
  <pubDate>{pub_date}</pubDate>
</item>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:nyt="http://www.nytimes.com/namespaces/rss/2.0" version="2.0">
<channel>
  <title>NYT &gt; Most Popular</title>
  {'\n'.join(map(guid_and_pub_date_to_xml, guid_and_pub_dates))}
</channel>
</rss>"""


class RssMergerTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
    
    def test_rss_merger(self):
        rss_text_1 = _nyt_rss_response([
            ('https://nyt.example.com/trump1.html', '2024-01-06T07:07:14+0000'),
            ('https://nyt.example.com/harris1.html', '2024-01-05T07:07:14+0000'),
        ])
        rss_text_2 = _nyt_rss_response([
            ('https://nyt.example.com/harris2.html', '2024-01-06T06:07:14+0000'),
            ('https://nyt.example.com/trump1.html', '2024-01-06T07:07:14+0000'),
        ])
        self.assertEqual(
            merger([rss_text_1, rss_text_2]),
            _nyt_rss_response([
                ('https://nyt.example.com/trump1.html', '2024-01-06T07:07:14+0000'),
                ('https://nyt.example.com/harris1.html', '2024-01-05T07:07:14+0000'),
                ('https://nyt.example.com/harris2.html', '2024-01-06T06:07:14+0000'),
            ])
        )
