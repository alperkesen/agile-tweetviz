
import os
import unittest
from TweetViz import app, db
from datetime import datetime
from TweetViz.sort import sort_by_retweets, sort_by_likes, \
    sort_by_text_length, sort_by_date
 
class Tweet:
    def __init__(self, full_text, favorite_count, retweet_count, created_at):
        self.full_text = full_text
        self.favorite_count = favorite_count
        self.retweet_count = retweet_count
        self.created_at = created_at
 
 
class SortTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        self.assertEqual(app.debug, False)

        self.tweets = [Tweet("This is a great day!", 10, 2,
                             datetime(2018, 4, 5)),
                       Tweet("100k", 200, 1, datetime(2019, 1, 3)),
                       Tweet("Thank you John, it was beautiful!",
                             1, 30, datetime(2000, 3, 3)),
                       Tweet("Anybody know how to cook lamb meat?", 500, 4,
                             datetime(2010, 1, 3))]
        
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_sort_page_get(self):
        response = self.app.get('/sort_tweets', follow_redirects=True)
        self.assertEqual(response.status_code, 405)

    def test_sort_by_retweets_ascended(self):
        sorted_tweets = sort_by_retweets(self.tweets, reverse=False)
        expected_result = [self.tweets[1],
                           self.tweets[0],
                           self.tweets[3],
                           self.tweets[2]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_retweets_descended(self):
        sorted_tweets = sort_by_retweets(self.tweets, reverse=True)
        expected_result = [self.tweets[2],
                           self.tweets[3],
                           self.tweets[0],
                           self.tweets[1]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_likes_ascended(self):
        sorted_tweets = sort_by_likes(self.tweets, reverse=False)
        expected_result = [self.tweets[2],
                           self.tweets[0],
                           self.tweets[1],
                           self.tweets[3]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_likes_descended(self):
        sorted_tweets = sort_by_likes(self.tweets, reverse=True)
        expected_result = [self.tweets[3],
                           self.tweets[1],
                           self.tweets[0],
                           self.tweets[2]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_text_length_ascended(self):
        sorted_tweets = sort_by_text_length(self.tweets, reverse=False)
        expected_result = [self.tweets[1],
                           self.tweets[0],
                           self.tweets[2],
                           self.tweets[3]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_text_length_descended(self):
        sorted_tweets = sort_by_text_length(self.tweets, reverse=True)
        expected_result = [self.tweets[3],
                           self.tweets[2],
                           self.tweets[0],
                           self.tweets[1]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_date_ascended(self):
        sorted_tweets = sort_by_date(self.tweets, reverse=False)
        expected_result = [self.tweets[2],
                           self.tweets[3],
                           self.tweets[0],
                           self.tweets[1]]

        self.assertEqual(sorted_tweets, expected_result)

    def test_sort_by_date_descended(self):
        sorted_tweets = sort_by_date(self.tweets, reverse=True)
        expected_result = [self.tweets[1],
                           self.tweets[0],
                           self.tweets[3],
                           self.tweets[2]]

        self.assertEqual(sorted_tweets, expected_result)

 
if __name__ == "__main__":
    unittest.main()
