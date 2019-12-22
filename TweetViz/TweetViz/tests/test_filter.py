import os
import unittest
import tweepy
from TweetViz import app
 
class FilterTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_tweepy_api(self):
        tweepyAuth = tweepy.OAuthHandler(
            "7kErkRN6gM6hauMct2Olqqwkq",
            "yuIZjc5Z5QCGjSss3X10sSBezWk08n4VKAnIumW4Fs5chr0LON")
        tweepyAuth.set_access_token(
            "3224914785-BwrhbViZQTo6KU3f7KDTHEstESQsM1P4euvlCii",
            "oMdYFV6sz9M5lNaSp5qXu7YQg1MruUraT8KXvmvJg3nTA")

        tweepyAPI = tweepy.API(tweepyAuth, wait_on_rate_limit=True)
        query = "test"
        limit = 20
        tweets = tweepy.Cursor(tweepyAPI.search, q=query,
                               tweet_mode="extended").items(limit)
        self.assertEqual(len([tweet for tweet in tweets]), limit)
        tweets = tweepy.Cursor(tweepyAPI.user_timeline, screen_name="POTUS", tweet_mode="extended").items(limit)
        self.assertEqual(len([tweet for tweet in tweets]), limit)

    def test_user_tweets(self):
        response = self.app.post('/filter_userTweets',
                                 data=dict(userName="POTUS"),
                                 follow_redirects=True)
        self.assertNotIn(b"Error", response.data)
        self.assertEqual(response.status_code, 200)


    def test_fake_user(self):
        response = self.app.post('/filter_userTweets',
                                 data=dict(userName="abcdeXYZ12345noUserExistsWithThisUserName"),
                                 follow_redirects=True)
        self.assertIn(b"Error", response.data)
        self.assertEqual(response.status_code, 200)

    def test_generic_query(self):
        response = self.app.post('/filter_genericSearch',
                                 data=dict(searchQuery="test"),
                                 follow_redirects=True)
        self.assertNotIn(b"Error", response.data)
        self.assertEqual(response.status_code, 200)

    def test_trend_topics(self):
        response = self.app.post('/filter_trendTopics_retrieve',
                                 follow_redirects=True)
        self.assertNotIn(b"Error", response.data)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
