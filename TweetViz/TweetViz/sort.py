from TweetViz import app
from flask import render_template, session, request
from .filter import createTable
from datetime import datetime


@app.route('/sort_tweets', methods=['POST'])
def sort_tweets():
    tweets = session.get('data')

    if request.form["action"] == "sort":
        sorting_method = request.form["sorting_method"]
        sorting_order = request.form["sorting_order"]

        reverse = True if sorting_order == "descended" else False

        if sorting_method == "retweets":
            sorted_tweets = sort_by_retweets(tweets, reverse)
        elif sorting_method == "likes":
            sorted_tweets = sort_by_likes(tweets, reverse)
        elif sorting_method == "text_length":
            sorted_tweets = sort_by_text_length(tweets, reverse)
        elif sorting_method == "date":
            sorted_tweets = sort_by_date(tweets, reverse)
        else:
            print("Invalid method!")
            sorted_tweets = tweets
    else:
        sorted_tweets = tweets

    session["data"] = sorted_tweets

    return render_template('/analysis/analysis.html', tableBody=createTable(sorted_tweets))


def sort_by_retweets(tweets, reverse=False):
    return sorted(tweets, key=lambda t: t.retweet_count, reverse=reverse)


def sort_by_likes(tweets, reverse=False):
    return sorted(tweets, key=lambda t: t.favorite_count, reverse=reverse)


def sort_by_text_length(tweets, reverse=False):
    return sorted(tweets, key=lambda t: len(t.full_text), reverse=reverse)


def sort_by_date(tweets, reverse=False):
    return sorted(tweets, key=lambda t: t.created_at, reverse=reverse)
