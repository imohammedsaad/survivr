import tweepy
import pymongo
from pymongo import MongoClient

# Twitter API credentials
api_key = 'SfTMnrV8aPb1xcMpzlE1eahe3'
api_secret_key = 'vy28N6P88OtTeGp0x5DnEa2peKjIppey5nPa7vwPUKmqA8vG7k'
access_token = '1730966855681257472-EbIGjOQoPglmz8thuBvHLPSKUsz22a'
access_token_secret = 'VtzMx23M8N7P8baLmNijEpYtyX8He2WJHYVooqERylfUQ'

# Authenticate with Twitter
auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.GeoNews
tweets_collection = db.tweets

# Define a function to fetch tweets
def fetch_tweets(keyword, count=100):
    tweets = api.search_tweets(q=keyword, count=count, lang='en')
    for tweet in tweets:
        data = {
            'text': tweet.text,
            'created_at': tweet.created_at,
            'location': tweet.user.location
        }
        tweets_collection.insert_one(data)

# Fetch disaster-related tweets
fetch_tweets("earthquake OR flood OR hurricane")
