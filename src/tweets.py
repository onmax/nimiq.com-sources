"""Computes sentiment analysis of tweets."""

import os

import requests
import argparse
from transformers import pipeline

from util import OUTPUT_FOLDER, get_contents, get_variable, set_contents

TWITTER_TOKEN = get_variable("TWITTER_TOKEN")


def fetch_tweets(query: str) -> list:
    """Fetch tweets from Twitter API."""
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "max_results": 100,
        "query": query,
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
        model="finiteautomata/bertweet-base-sentiment-analysis",
        truncation=True)
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
    old_tweets_list = get_contents(filename)

    # Append new items
    old_url = [tweet["tweet"]["url"] for tweet in old_tweets_list]
    for tweet in tweets_list:
        if tweet["tweet"]["url"] not in old_url:
            old_tweets_list.append(tweet)

    print(f"Saving {len(filename)} tweets in {filename}")
    set_contents(filename, old_tweets_list)

def main(query: str, output: str):
    if "-is:retweet" not in query:
        query += " -is:retweet"

    tweets = parse_tweets(fetch_tweets(query))
    sentiments = compute_sentiment(tweets)
    for tweet, sentiment in zip(tweets, sentiments):
        tweet["sentiment"] = sentiment
    positive_tweets = filter_positive_tweets(tweets, sentiments, 0.7)

    filename_tweets = os.path.join(OUTPUT_FOLDER, output, "tweets.json")
    append_new_items(tweets, filename_tweets)

    filename_positive = os.path.join(OUTPUT_FOLDER, output, "positive-tweets.json")
    append_new_items(positive_tweets, filename_positive)

parser = argparse.ArgumentParser(
    prog='Tweets Fetcher',
    description='Fetch tweets from Twitter API and compute sentiment analysis.',
    epilog='Enjoy the program! :)')
parser.add_argument('-q', '--query', required=True, help='Query to search for')
parser.add_argument('-o', '--output', required=True, help='Output folder under output/')
args = parser.parse_args()
main(args.query, args.output)
