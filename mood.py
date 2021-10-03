from numpy import result_type
import tweepy
import pandas as pd
import numpy as np
import re
from textblob import TextBlob
from datetime import datetime
import time
import pytz
import config

# Authenticate to Twitter
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)

# Create API instance 
api = tweepy.API(auth)

# User's twitter handle we'll be analyzing
user_handle = "@elonmusk"

# Get a user's tweets for the past 30 days
def get_tweets(api, username) -> list[str]:
    days_created : list[int] = []
    tweets_list : list[str] = []
    tweets = tweepy.Cursor(api.user_timeline, screen_name=user_handle).items()
    for tweet in tweets:
        if not tweet.retweeted and abs(datetime.now() - tweet.created_at.replace(tzinfo=None)).days < 30:
            #days_created.append(tweet.created_at.day)
            tweets_list.append(tweet.text)
    return days_created, tweets_list

days_created = get_tweets(api, user_handle)[0]
tweets = get_tweets(api, user_handle)[1]

print(f"{len(days_created)} and {len(tweets)}")

# Create a dataframe
df = pd.DataFrame(tweets, columns=["Tweets"])

# Clean the data
def clean_tweet(tweet):
    tweet = re.sub(r"@[A-Za-z0-9]+", "", tweet) # removes @ mentions
    tweet = re.sub(r"#", "", tweet) # removes the # symbol
    tweet = re.sub(r"RT[\s]+", "", tweet) # removes retweets
    tweet = re.sub(r"https?:\/\/\S+", "", tweet) # removes links

    return tweet

# Create day_created column in dataframe
#print(days_created)
#df["Days"] = days_created

# Clean tweets in the 'Tweets' column
df["Tweets"] = df["Tweets"].apply(clean_tweet)
df = df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii')) # remove emojis
df.replace(r'^\s*$', np.nan, regex=True)

# Get subjectivity of tweet
def get_subjectivity(tweet):
    return TextBlob(tweet).sentiment.subjectivity

# Get polarity of tweet
def get_polarity(tweet):
    return TextBlob(tweet).sentiment.polarity

# Create two new dataframe columns: subjectivity and polarity
df["Subjectivity"] = df["Tweets"].apply(get_subjectivity)
df["Polarity"] = df["Tweets"].apply(get_polarity)

# Get sentiment (positive, negative or neutral) of tweet
def getSentiment(score):
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"

# Create sentiment column in dataframe
df["Sentiment"] = df["Polarity"].apply(getSentiment)

print(df)