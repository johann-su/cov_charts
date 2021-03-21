import os
import random

import requests
import tweepy

# http://developer.zeit.de/
# TODO: Insert API Key
# zeit_news = requests.get('http://api.zeit.de/content?q=covid', headers={'X-Authorization': os.getenv('ZEIT_API_KEY')}).text

# print(zeit_news)

auth = tweepy.OAuthHandler(os.getenv('TWITTER_KEY'), os.getenv('TWITTER_SECRET'))
auth.set_access_token(os.getenv('TWITTER_AT'), os.getenv('TWITTER_ATS'))

api = tweepy.API(auth)

public_tweets = api.user_timeline('@rki_de', count=10) # @c_drosten, 

id = random.randint(0, 10)

print(public_tweets[id])