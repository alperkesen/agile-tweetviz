
from flask import render_template, request, session, redirect, url_for, flash
from flask import Markup
from TweetViz import app
from flask_recaptcha import ReCaptcha
from flask_login import current_user
import tweepy
from . import tweepyAPI
from . import recaptcha
from .static import home

def createTable(tweets, cache=0):
    counter = 0
    markup = ''
    data = []

    status = 0
    # Reply count not available per API allowances.
    try:
        for tweet in tweets:
            try:
                favCount = tweet.favorite_count
                if hasattr(tweet, 'retweeted_status'):
                    favCount = tweet.retweeted_status.favorite_count
                place = 'N/A'
                if hasattr(tweet, 'place') and hasattr(tweet.place, 'name'):
                    place = tweet.place.name

                markup += """<tr>
                                <td>{0}</td>
                                <td>{1}</td>
                                <td>{2}</td>
                                <td>{3}</td>
                                <td>{4}</td>
                                <td>{5}</td>
                                <td>{6}</td>
                                <td>{7}</td>
                             </tr>""".format(counter,
                                   tweet.created_at,
                                   tweet.user.name,
                                   tweet.full_text,
                                   tweet.lang,
                                   place,
                                   tweet.retweet_count,
                                   favCount)
                counter += 1
                if(cache == 1):
                    data.append(tweet)    
            
            except:
                status = 1
                pass
    except tweepy.TweepError as e:
        if status == 0:
            return e.reason

    if counter == 0:
        return "No Tweet was found!"

    if(cache == 1):
        session['data'] = data

    return Markup(markup)


def retrieveTweets(mode=0, query=''):
    limit = 150
    if not current_user.is_authenticated:
        limit = 25

    if mode==1:
        tweets = tweepy.Cursor(tweepyAPI.user_timeline, screen_name=query, tweet_mode="extended").items(limit)
    else:
        tweets = tweepy.Cursor(tweepyAPI.search, q=query, tweet_mode="extended").items(limit)

    return createTable(tweets, 1)


@app.route('/filter_genericSearch', methods=['POST'])
def filter_genericSearch(query='', safe=0):
    
    if app.config['TESTING'] == False and (not current_user.is_authenticated) and (safe==0):
       return redirect(url_for('home'))

    if query == '':
        query = request.form.get('searchQuery');
    
    tweets = retrieveTweets(0, query)

    if not isinstance(tweets, Markup):
        flash(tweets)
        return redirect(url_for('home'))

    return render_template('/parse/parse.html', tableBody=tweets)


@app.route('/filter_userTweets', methods=['POST'])
def filter_userTweets():
    if app.config['TESTING'] == False and not (recaptcha.verify() or current_user.is_authenticated):
        return redirect(url_for('home'))

    userName = request.form.get('userName')

    tweets = retrieveTweets(1, userName)

    if not isinstance(tweets, Markup):
        flash(tweets)
        return redirect(url_for('home'))

    return render_template('/parse/parse.html', tableBody=tweets)


@app.route('/filter_trendTopics_retrieve', methods=['POST'])
def filter_trendTopicsRetrieve():
    if app.config['TESTING'] == False and not (recaptcha.verify() or current_user.is_authenticated):
        return redirect(url_for('home'))

    trends1 = tweepyAPI.trends_place(1)
    data = trends1[0] 
    trends = data['trends']
    names = [trend['name'] for trend in trends]

    htmlCode = ''
    for separate in names:
        htmlCode += """<a href="/filter_trendTopics?tt=$" class="list-group-item">$</a>""".replace("$", separate.replace("#",''))
        
    if htmlCode == '':
        flash('No Trend Topic was found!')
        return redirect(url_for('home'))

    return render_template('/filter/trendTopics.html', ttList=Markup(htmlCode))

@app.route('/filter_trendTopics', methods=['GET'])
def filter_trendTopics():
    qStr = request.args.get('tt')
    return filter_genericSearch('#' + qStr, safe=1) 
