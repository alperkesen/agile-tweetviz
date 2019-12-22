"""
    Agile TweetViz
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_recaptcha import ReCaptcha
from flask_kvsession import KVSessionExtension
from simplekv.db.sql import SQLAlchemyStore
import tweepy
import os
from flaskext.csrf import csrf


app = Flask(__name__)

recaptcha = ReCaptcha(app=app)

app.config['TESTING'] = False
app.config['BASEDIR'] = os.path.dirname(os.path.abspath(__file__))
app.config['SECRET_KEY'] = 'TweetVizRandomKey123321'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)
db.init_app(app)

store = SQLAlchemyStore(db.engine, db.metadata, 'sessions')
kvsession = KVSessionExtension(store, app)

login_manager = LoginManager()
login_manager.login_view = 'views.login'
login_manager.init_app(app)

csrf(app)

tweepyAuth = tweepy.OAuthHandler("7kErkRN6gM6hauMct2Olqqwkq", 
    "yuIZjc5Z5QCGjSss3X10sSBezWk08n4VKAnIumW4Fs5chr0LON")
tweepyAuth.set_access_token("3224914785-BwrhbViZQTo6KU3f7KDTHEstESQsM1P4euvlCii", 
    "oMdYFV6sz9M5lNaSp5qXu7YQg1MruUraT8KXvmvJg3nTA")

tweepyAPI = tweepy.API(tweepyAuth, wait_on_rate_limit=True)

app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "6Le9bcUUAAAAAPQdEAJG216yCxdVj_PqJXBbotYc",
    RECAPTCHA_SECRET_KEY = "6Le9bcUUAAAAALSfrdq9rsZylOoHGdT3Apef3B1D",
))

recaptcha = ReCaptcha()
recaptcha.init_app(app)

mapbox_access_token = 'pk.eyJ1Ijoic2VyYXR0IiwiYSI6ImNrNGZ1anV0ejBxOXozZW83MWZ1b3d5NWsifQ.lbad3stoMzZ2waaS9eC2dA'

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# db.create_all() # Use when needed

import TweetViz.static
import TweetViz.auth
import TweetViz.filter
import TweetViz.parse
import TweetViz.sort
import TweetViz.analyze

