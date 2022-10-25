"""Computes sentiment analysis of tweets."""

import json
import os

import requests
from transformers import pipeline

TWITTER_TOKEN = os.environ.get("TWITTER_TOKEN")

if TWITTER_TOKEN is None:
    print("Please set the TWITTER_TOKEN environment variable.")
    exit(1)


def fetch_tweets() -> list:
    """Fetch tweets from Twitter API."""
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "max_results": 100,
        "query": "nimiq -is:retweet",
        "tweet.fields": "created_at",
        "expansions": "author_id",
        "user.fields": "profile_image_url",
    }
    headers = {
        "Authorization": f"Bearer {TWITTER_TOKEN}",
    }
    response = requests.get(url, params=params, headers=headers, timeout=10)
    return response.json()


def parse_tweets(res: list) -> list:
    """Convert Twitter's response to our structure."""
    tweets_list = []
    users = res["includes"]["users"]
    for tweet in res["data"]:
        user = next(user for user in users if user["id"] == tweet["author_id"])
        url = f"https://twitter.com/{user['username']}/status/{tweet['id']}"
        tweets_list.append({
            "tweet": {
                "content": tweet["text"],
                "url": url,
                "created_at": tweet["created_at"],
            },
            "user": {
                "username": user["username"],
                "profile_image_url": user["profile_image_url"],
            },
            "sentiment": None,
        })
    return tweets_list


def compute_sentiment(tweets_list: list) -> list:
    """Compute the sentiment analysis."""
    sentiment_pipeline = pipeline(
        model="finiteautomata/bertweet-base-sentiment-analysis")
    sentences = [tweet["tweet"]["content"] for tweet in tweets_list]
    return sentiment_pipeline(sentences)


def filter_positive_tweets(
        tweets_list: list, sentiments_list: list, threshold: float) -> list:
    """Filter the positive tweets."""
    res = []
    for tweet, sentiment in zip(tweets_list, sentiments_list):
        if sentiment["score"] >= threshold:
            res.append(tweet)
    return res


def append_new_items(tweets_list: list, filename: str) -> None:
    """Append new items to the json file."""
    filename = os.path.join("./output/tweets", filename)
    old_tweets_list = []

    # Open the file. If file does not exist, create it.
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as fi:
            old_tweets_list = json.load(fi)

    # Append new items
    old_url = [tweet["tweet"]["url"] for tweet in old_tweets_list]
    for tweet in tweets_list:
        if tweet["tweet"]["url"] not in old_url:
            old_tweets_list.append(tweet)

    if not os.path.exists("output"):
        os.makedirs("output")
    if not os.path.exists("output/tweets"):
        os.makedirs("output/tweets")

    # Save the new list
    with open(filename, "w", encoding="utf-8") as fi:
        print(f"Saving {len(old_tweets_list)} tweets in {filename}")
        json.dump(old_tweets_list, fi, indent=2)


tweets = parse_tweets(fetch_tweets())
sentiments = compute_sentiment(tweets)
positive_tweets = filter_positive_tweets(tweets, sentiments, 0.7)

append_new_items(tweets, "tweets.json")
append_new_items(positive_tweets, "positives-tweets.json")
