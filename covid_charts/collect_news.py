import os
import random

import json
import requests
import tweepy

def get_articles():
    # http://developer.zeit.de/
    zeit_news = requests.get('http://api.zeit.de/content?q=covid', headers={'X-Authorization': os.getenv('ZEIT_API_KEY')}).text

    zeit_news = json.loads(zeit_news)

    return zeit_news['matches']

def get_tweets():
    auth = tweepy.OAuthHandler(os.getenv('TWITTER_KEY'), os.getenv('TWITTER_SECRET'))
    auth.set_access_token(os.getenv('TWITTER_AT'), os.getenv('TWITTER_ATS'))

    api = tweepy.API(auth)

    public_tweets = api.user_timeline('@rki_de', count=10) # @c_drosten, 

    return public_tweets