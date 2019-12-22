import os
import unittest
from TweetViz import app, db
from TweetViz.analyze import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
 
TEST_DB = 'test.db'


class Place:
    def __init__(self, name):
        self.name = name


class Tweet:
    def __init__(self, full_text="", favorite_count=0,
                 retweet_count=0, created_at=datetime.now(),
                 place=None, hashtags=list()):
        self.full_text = full_text
        self.favorite_count = favorite_count
        self.retweet_count = retweet_count
        self.created_at = created_at
        self.place = place
        self.entities = {"hashtags": hashtags}

 
class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

        self.assertEqual(app.debug, False)

        self.tweets = [Tweet(place=Place("Istanbul"),
                             hashtags=[{"text": "Turkey"},
                                       {"text": "Sultanahmet"},
                                       {"text": "Cennet"}],
                             created_at=datetime(2020, 1, 1),
                             favorite_count=15,
                             retweet_count=0),
                       Tweet(place=Place("Los Angeles"),
                             hashtags=[{"text": "Santa Monica"},
                                       {"text": "Hollywood"},
                                       {"text": "Cennet"}],
                             created_at=datetime(2018, 1, 1),
                             favorite_count=0,
                             retweet_count=60000),
                       Tweet(place=Place("Yozgat"),
                             hashtags=[{"text": "Turkey"},
                                       {"text": "Cennet"}],
                             created_at=datetime(2012, 5, 1),
                             favorite_count=3,
                             retweet_count=0),
                       Tweet(place=Place("Yozgat"),
                                  created_at=datetime(2018, 3, 1),
                             favorite_count=400,
                             retweet_count=15000),
                       Tweet(place=Place("Los Angeles"),
                             hashtags=[{"text": "UCLA"}],
                             created_at=datetime(2018, 12, 1),
                             favorite_count=2000,
                             retweet_count=7),
                       Tweet(place=Place("Yozgat"),
                             created_at=datetime(2020, 11, 1),
                             favorite_count=105,
                             retweet_count=3),
                       Tweet(created_at=datetime(2005, 12, 1),
                             favorite_count=35,
                             retweet_count=30000)]

    def tearDown(self):
        pass

    def test_analyze_by_location(self):
        locations_dict = analyze_by_location(self.tweets)

        self.assertEqual(len(locations_dict["Istanbul"]), 1)
        self.assertEqual(len(locations_dict["Yozgat"]), 3)
        self.assertEqual(len(locations_dict["no_location"]), 1)
        self.assertEqual(len(locations_dict["Los Angeles"]), 2)

    def test_analyze_by_hashtag(self):
        hashtags_dict = analyze_by_hashtag(self.tweets)

        self.assertEqual(hashtags_dict["Turkey"], 2)
        self.assertEqual(hashtags_dict["Hollywood"], 1)
        self.assertEqual(hashtags_dict["UCLA"], 1)
        self.assertEqual(hashtags_dict["Santa Monica"], 1)
        self.assertEqual(hashtags_dict["Sultanahmet"], 1)
        self.assertEqual(hashtags_dict["Cennet"], 3)

    def test_analyze_by_year(self):
        years_dict = analyze_by_year(self.tweets)

        self.assertEqual(years_dict[2020], 2) 
        self.assertEqual(years_dict[2018], 3)
        self.assertEqual(years_dict[2005], 1)
        self.assertEqual(years_dict[2012], 1)

    def test_analyze_by_month(self):
        months_dict = analyze_by_month(self.tweets)

        self.assertEqual(months_dict[1], 2)
        self.assertEqual(months_dict[12], 2)
        self.assertEqual(months_dict[3], 1)
        self.assertEqual(months_dict[11], 1)
        self.assertEqual(months_dict[5], 1)

    def test_analyze_by_likes(self):
        likes_dict = analyze_by_like(self.tweets)

        self.assertEqual(likes_dict["No favorite"], 1)
        self.assertEqual(likes_dict["Low favorite count (>0)"], 1)
        self.assertEqual(likes_dict["Average favorite count (>10)"], 2)
        self.assertEqual(likes_dict["High favorite count (>100)"], 2)
        self.assertNotIn("Very high favorite count (>1000)", likes_dict)
        self.assertEqual(likes_dict["Top favorite count (>10000)"], 1)

    def test_analyze_by_retweets(self):
        retweets_dict = analyze_by_retweet(self.tweets)

        self.assertEqual(retweets_dict["No retweet"], 2)
        self.assertEqual(retweets_dict["Low retweet count (>0)"], 2)
        self.assertNotIn("Average retweet count (>10)", retweets_dict)
        self.assertNotIn("High retweet count (>100)", retweets_dict)
        self.assertNotIn("Very high retweet count (>1000)", retweets_dict)
        self.assertEqual(retweets_dict["Top retweet count (>10000)"], 3)

    def test_sentiment_analysis(self):
        tweets = [
            "@john it was great suggestion John",
            "It was horrible movie that I have ever seen",
            "I really love listening to the metal music"
        ]

        ground_truth = [1, 0, 1]

        sid = SentimentIntensityAnalyzer()
        sentiments = [predict_sentiment(sid.polarity_scores(tweet))
                      for tweet in tweets]

        self.assertEqual(sentiments, ground_truth)



if __name__ == "__main__":
    unittest.main()
