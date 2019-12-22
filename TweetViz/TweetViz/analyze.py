import nltk
import json
from flask import Markup, render_template, request, session
from TweetViz import app
from .filter import createTable
from flask_login import current_user
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from . import mapbox_access_token


@app.route('/analyze_tweets', methods=['GET', 'POST'])
def analyzeTweets():
    tweets = session.get('data')
    analyze_methods = request.form.getlist('analyze_method')

    results = ""
    charts = ""

    if not "rtEval" in analyze_methods:
        tweets[:] = [x for x in tweets if not x.full_text.startswith("RT")]

    word_json = list()

    panelTemplate = """<div class="row" style="padding: 0px 25px 25px 25px;">
                    <div class="panel panel-default">
                        <div class="panel-heading">{}</div>
                        <div class="panel-body">
                            <div id={} style="width: 900px; height: 500px;" class="center-block"></div>
                        </div>
                    </div>
                </div>"""

    
    if "heatmap" in analyze_methods:
        script = get_map(tweets)
        results += script
    if "sentiment" in analyze_methods and current_user.is_authenticated:
        tweets2 = []
        for tweet in tweets:
            if hasattr(tweet, 'lang'):
                if tweet.lang == "en":
                    tweets2.append(tweet)

        sentiments = analyze_sentiment(tweets2)

        num_pos_tweets = sum(sentiments)
        num_neg_tweets = len(sentiments) - num_pos_tweets
        div_id = "sentiment_analysis"

        results += panelTemplate.format('Sentiments', div_id)

        statistics_dict = {"Positive": num_pos_tweets,
                           "Negative": num_neg_tweets}

        criteria = "Sentiment"
        title = "Sentiment Analysis"

        chart = draw_pie_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    if "location" in analyze_methods:
        locations_dict = analyze_by_location(tweets)

        div_id = "location_analysis"
        results += panelTemplate.format('Location', div_id)

        statistics_dict = {c: len(locations_dict[c]) for c in locations_dict}

        criteria = "Location"
        title = "Location Analysis"

        chart = draw_bar_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    if "hashtag" in analyze_methods:
        hashtags_dict = analyze_by_hashtag(tweets)
        statistics_dict = hashtags_dict

        div_id = "hashtag_analysis"
        results += panelTemplate.format('Hashtag', div_id)

        criteria = "Hashtag"
        title = "Hashtag Analysis"

        chart = draw_bar_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    if "year" in analyze_methods:
        years_dict = analyze_by_year(tweets)
        statistics_dict = years_dict

        div_id = "year_analysis"
        results += panelTemplate.format('Year', div_id)

        criteria = "Year"
        title = "Year Analysis"

        chart = draw_bar_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    if "month" in analyze_methods:
        months_dict = analyze_by_month(tweets)
        statistics_dict = months_dict

        div_id = "month_analysis"
        results += panelTemplate.format('Month', div_id)

        criteria = "Month"
        title = "Month Analysis"

        chart = draw_bar_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    if "word_cloud" in analyze_methods:
        word_json = analyze_word_cloud(tweets)

        div_id = "word_cloud"
        results += panelTemplate.format('Word Cloud', div_id)

    if "like" in analyze_methods:
        statistics_dict = analyze_by_like(tweets)

        title = "Like Analysis"
        div_id = "likes"
        criteria = "Like class"

        results += panelTemplate.format(criteria, div_id)

        chart = draw_bar_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    if "retweet" in analyze_methods:
        statistics_dict = analyze_by_retweet(tweets)

        title = "Retweet Analysis"
        div_id = "retweets"
        criteria = "Retweet class"

        results += panelTemplate.format(criteria, div_id)

        chart = draw_bar_chart(title, criteria, statistics_dict, div_id)
        charts += chart

    session.pop('data')
    results = Markup(results)
    return render_template('/analysis/result.html',
                           tableBody=createTable(tweets),
                           results=results,
                           charts=charts,
                           word_json=word_json,
                           mapbox_access_token=mapbox_access_token)


def analyze_sentiment(tweets):
    try:
        sid = SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download("vader_lexicon")
        sid = SentimentIntensityAnalyzer()

    sentiments = [predict_sentiment(sid.polarity_scores(tweet.full_text))
                  for tweet in tweets]

    return sentiments


def predict_sentiment(scores):
    return 1 if scores["pos"] >= scores["neg"] else 0


def analyze_by_location(tweets):
    locations = set([tweet.place.name for tweet in tweets if tweet.place])

    locations_dict = {location: [tweet for tweet in tweets
                                 if tweet.place and
                                 tweet.place.name == location]
                      for location in locations}

    locations_dict["no_location"] = [tweet for tweet in tweets
                                     if tweet.place == None]

    return locations_dict


def analyze_by_hashtag(tweets):
    hashtags_dict = dict()

    for tweet in tweets:
        hashtags = tweet.entities["hashtags"]

        hashtags = set([hashtag["text"] for hashtag in hashtags])

        for hashtag in hashtags:
            hashtags_dict[hashtag] = 1 + hashtags_dict.get(hashtag, 0)

    return hashtags_dict


def analyze_by_year(tweets):
    years = list(tweet.created_at.timetuple().tm_year for tweet in tweets)
    years_dict = {year: years.count(year) for year in set(years)}

    return years_dict


def analyze_by_month(tweets):
    months = list(tweet.created_at.timetuple().tm_mon for tweet in tweets)
    months_dict = {month: months.count(month) for month in set(months)}

    return months_dict


def analyze_by_retweet(tweets):
    retweets_list = list()

    for tweet in tweets:
        if tweet.retweet_count == 0:
            retweet_status = "No retweet"
        elif tweet.retweet_count < 10:
            retweet_status = "Low retweet count (>0)"
        elif tweet.retweet_count < 100:
            retweet_status = "Average retweet count (>10)"
        elif tweet.retweet_count < 1000:
            retweet_status = "High retweet count (>100)"
        elif tweet.retweet_count < 10000:
            retweet_status = "Very high retweet count (>1000)"
        else:
            retweet_status = "Top retweet count (>10000)"

        retweets_list.append(retweet_status)

    retweets_dict = {status: retweets_list.count(status)
                     for status in set(retweets_list)}

    return retweets_dict


def analyze_by_like(tweets):
    likes_list = list()

    for tweet in tweets:
        if tweet.favorite_count == 0:
            like_status = "No favorite"
        elif tweet.favorite_count < 10:
            like_status = "Low favorite count (>0)"
        elif tweet.favorite_count < 100:
            like_status = "Average favorite count (>10)"
        elif tweet.favorite_count < 1000:
            like_status = "High favorite count (>100)"
        elif tweet.favorite_count < 1000:
            like_status = "Very high favorite count (>1000)"
        else:
            like_status = "Top favorite count (>10000)"

        likes_list.append(like_status)

    likes_dict = {status: likes_list.count(status)
                  for status in set(likes_list)}

    return likes_dict


def analyze_word_cloud(tweets):
    words = [word.lower() for tweet in tweets for word in tweet.full_text.split()]
    words = filter_words(words)

    words_dict = {word: words.count(word) for word in set(words)}
    word_freqs = [{"text": word, "weight": str(words_dict[word])}
                  for word in words_dict]
    word_freqs = remove_less_frequent(word_freqs)

    word_json = json.dumps(word_freqs)

    return word_json


def remove_less_frequent(word_freqs, threshold=5):
    return [word for word in word_freqs if int(word["weight"]) < threshold]


def filter_words(words):
    filtered_words = remove_stopwords(words)
    filtered_words = remove_retweets(filtered_words)
    filtered_words = remove_links(filtered_words)
    filtered_words = remove_hashtags(filtered_words)
    filtered_words = remove_mentions(filtered_words)

    return filtered_words


def remove_stopwords(words):
    try:
        stop_words = set(stopwords.words('english'))
    except LookupError:
        nltk.download("stopwords")
        stop_words = set(stopwords.words('english'))

    filtered_words = [word for word in words if not word in stop_words]

    return filtered_words


def remove_retweets(words):
    filtered_words = [word for word in words if not word == "rt"]

    return filtered_words


def remove_links(words):
    filtered_words = [word for word in words if not word.startswith("http")]

    return filtered_words


def remove_hashtags(words):
    filtered_words = [word for word in words if not word.startswith("#")]

    return filtered_words


def remove_mentions(words):
    filtered_words = [word for word in words if not word.startswith("@")]

    return filtered_words


def draw_pie_chart(title, criteria, statistics_dict, div_id):
    data_table = str([[str(c).capitalize(), statistics_dict[c]]
                      for c in statistics_dict])[1:-1]

    chart_script = """
      google.charts.load('current', {{'packages':['corechart']}});
      google.charts.setOnLoadCallback(drawChart{3});

      function drawChart{3}() {{

        var data{3} = google.visualization.arrayToDataTable([
          ['{0}', 'Number of Tweets'],
          {1}
        ]);

        var options{3} = {{
          title: '{2}'
        }};

        var chart{3} = new google.visualization.PieChart(document.getElementById('{3}'));

        chart{3}.draw(data{3}, options{3});
      }}""".format(criteria.capitalize(), data_table, title, div_id)

    return chart_script


def draw_bar_chart(title, criteria, statistics_dict, div_id):
    data_table = str([[str(c).capitalize(), statistics_dict[c]]
                      for c in statistics_dict])[1:-1]

    chart_script = """
      google.charts.load('current', {{packages: ['corechart', 'bar']}});
      google.charts.setOnLoadCallback(drawBasic{4});

      function drawBasic{4}() {{

        var data{4} = google.visualization.arrayToDataTable([
          ['{0}', 'Number of Tweets',],
          {1}
      ]);

      var options{4} = {{
        title: '{2}',
        chartArea: {{width: '50%'}},
        hAxis: {{
          title: 'Number of Tweets',
          minValue: 0
        }},
        vAxis: {{
          title: '{3}'
        }}
      }};

      var chart{4} = new google.visualization.BarChart(document.getElementById('{4}'));

      chart{4}.draw(data{4}, options{4});
    }}""".format(criteria, data_table, title, criteria, div_id)

    return chart_script

def get_map(tweets):
    map_script = ""
    map_script += """


                        <div class="row" style="padding: 0px 25px 25px 25px;">
                    <div class="panel panel-default">
                        <div class="panel-heading">Heatmap</div>
                        <div class="panel-body">
                            <div id=heatmap style="width: 900px; height: 500px;" class="center-block">
                            <!--  Heatmap  -->

                        <div id="map"></div>
                        <script>
                            window.addEventListener('load',()=>{
                                var token = document.getElementById('token')


                            mapboxgl.accessToken = token.value;
                            var map = new mapboxgl.Map({
                                container: 'map',
                                style: 'mapbox://styles/mapbox/outdoors-v11',
                                center: [40, 40.492392],
                                zoom: 1.2
                            });

                            map.on('load', function() {
                                map.addSource('tweet-locations', {
                                    'type': 'geojson',
                                    'data': {
                                        'type': 'FeatureCollection',
                                        'features': ["""

    for tweet in tweets:
        try:
            bbox = tweet.place.bounding_box.coordinates
            lon = bbox[0][0][0]
            lat = bbox[0][0][1]

            map_script += """
                            {{
                                'type': 'Feature',
                                'geometry': {{
                                'type': 'Point',
                                'coordinates': [{}, {}]
                                }}
                            }},""".format(lon, lat)
        except:
            pass

    map_script += """
                            ]
                        }
                    });

                    

                    map.addLayer({
                        'id': 'loc',
                        'type': 'circle',
                        'source': 'tweet-locations',
                        'paint': {
                            'circle-radius': 6,
                            'circle-color': '#B42222'
                        },
                        'filter': ['==', '$type', 'Point']
                    });
                });
                });
        </script>
                            </div>
                        </div>
                    </div>
                </div>"""



    return map_script
        

