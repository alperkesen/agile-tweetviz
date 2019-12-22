from flask import render_template, session, request
from TweetViz import app
from .filter import createTable
from .analyze import analyzeTweets
import re

def parseTweets(tweets, pattern):
    parsedTweets = []
    for tweet in tweets:
        try:
            content = tweet.full_text
            isMatched = re.search(pattern, content)
            if(isMatched):
                parsedTweets.append(tweet)        
        except:
            return 0

    session['data'] = parsedTweets

    return parsedTweets


@app.route('/parse_skip', methods=['POST'])
def parseSkip():
    filteredTweets = session.get('data')
    return render_template('/sort/sort.html', tableBody=createTable(filteredTweets))

@app.route('/parse_analyze', methods=['POST'])
def parseAndAnalyze():
    filteredTweets = session.get('data')

    pattern = request.form.get('regularExpression')

    if pattern == '':
        return render_template('/analysis/analysis.html', tableBody=createTable(filteredTweets))
        
    parsedTweets = parseTweets(filteredTweets, pattern)

    if parsedTweets == 0:
        flash("Parsing error! Try again.")
        return redirect(url_for('home'))

    return render_template('/analysis/analysis.html', tableBody=createTable(parsedTweets))


# Parse and continue with sorting
@app.route('/parse', methods=['POST'])
def parseAndSort():
    filteredTweets = session.get('data')

    pattern = request.form.get('regularExpression')

    if pattern == '':
        return parseSkip()

    parsedTweets = parseTweets(filteredTweets, pattern)

    if parsedTweets == 0:
        flash("Parsing error! Try again.")
        return redirect(url_for('home'))

    return render_template('/sort/sort.html', tableBody=createTable(parsedTweets))
