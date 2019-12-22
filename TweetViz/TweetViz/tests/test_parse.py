import os
import unittest
import tweepy
from TweetViz import app
import re 

class ParseTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

    def tearDown(self):
        pass

    def test_parse(self):
        pattern = "^The"
        content = "Test 1"
        content2 = "The test"
        isMatched = re.search(pattern, content)
        self.assertEqual(isMatched, None)
        isMatched = re.search(pattern, content2)
        self.assertNotEqual(isMatched, None)

if __name__ == "__main__":
    unittest.main()
