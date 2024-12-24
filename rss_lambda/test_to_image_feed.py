import unittest
from .to_image_feed.to_image_feed import to_image_feed
from .test_utils import nitter_rss20_response


class ToImageFeedTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_to_image_feed(self):
        rss_text = nitter_rss20_response([
            '<p>some random text</p>',
            '<p>also some random texts</p><p>but without images haha</p>',
            '<p>also some random texts<br>but without images haha 2222</p> ',
            '<p>also some random texts but with images hahahaha</p><img src="https://nitter.example.com/twitter_handle/pic/pic1.jpg" /><img src="https://nitter.example.com/twitter_handle/pic/pic2.jpg" />',
            '<p>also some random texts but with images hahahaha</p><img src="https://nitter.example.com/twitter_handle/pic/pic3.jpg" />',
        ])
        self.assertEqual(
            to_image_feed(rss_text),
            nitter_rss20_response([
                '<img src="https://nitter.example.com/twitter_handle/pic/pic1.jpg"></img>',
                '<img src="https://nitter.example.com/twitter_handle/pic/pic2.jpg"></img>',
                '<img src="https://nitter.example.com/twitter_handle/pic/pic3.jpg"></img>',
            ])
        )
