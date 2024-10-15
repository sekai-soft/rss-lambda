import shutil
import unittest
import unittest.mock
from .test_utils import nitter_rss20_response


class ImageRecognitionTestCase(unittest.TestCase):
    def setUp(self):
        shutil.rmtree('cache')
        self.maxDiff = None

    @unittest.mock.patch('rss_lambda.rss_image_recognition._download_image')
    @unittest.mock.patch('rss_lambda.yolov3.yolov3')
    def test_image_recognition(
        self,
        mocked_download_image,
        mocked_yolov3):
        rss_text = nitter_rss20_response([
            '<p>some random text</p>',
            '<p>also some random texts</p><p>but without images haha</p>',
            '<p>also some random texts<br>but without images haha 2222</p> ',
            '<p>also some random texts but with images hahahaha</p><img src="https://nitter.example.com/twitter_handle/pic/pic1.jpg" /><img src="https://nitter.example.com/twitter_handle/pic/pic2.jpg" />',
            '<p>also some random texts but with images hahahaha</p><img src="https://nitter.example.com/twitter_handle/pic/pic3.jpg" />',
        ])
