"""Get some values from from LunarCrush."""

import datetime
import requests

from util import OUTPUT_FOLDER, get_variable, set_contents

LUNARCRUSH_TOKEN = get_variable("LUNARCRUSH_TOKEN")

headers = {
    "Authorization": f"Bearer {LUNARCRUSH_TOKEN}",
}

# Docs: https://lunarcrush.com/developers/api/coins/:coin
URL = "https://lunarcrush.com/api3/coins/NIM"

response = requests.request("GET", URL, headers=headers, timeout=10)
# print type of response.text

if response.status_code != 200:
    raise Exception(f"Error: {response.status_code}")

data = response.json()["data"]

#  Sum of followers, retweets, likes, reddit karma... of social posts collected
social_score = data["social_score"]

# Position/rank of the assets 24 hour social score relative to all other
# supported assets, lower is best/highest social score
social_score_24h_rank = data["social_score_24h_rank"]

# Average sentiment of collected social posts
average_sentiment = data["average_sentiment"]

# Percent of bullish or very bullish tweets
sentiment_absolute = data["sentiment_absolute"]

# Percent tweets that are bullish (excluding neutral in the count)
sentiment_relative = data["sentiment_relative"]

# A proprietary score based on the relative trend of social_score
social_impact_score = data["social_impact_score"]

# A proprietary score based on technical indicators of price, average
# social sentiment, relative social activity
galaxy_score = data["galaxy_score"]

# The number of unique accounts posting on social
social_contributors = data["social_contributors"]

# Number of social posts over the last 24 hours
social_volume_calc_24h = data["social_volume_calc_24h"]

# Sum of social engagement over the last 24 hours
social_score_calc_24h = data["social_score_calc_24h"]

data = {
    "date": datetime.datetime.now().isoformat(),
    "social_score": social_score,
    "social_score_24h_rank": social_score_24h_rank,
    "average_sentiment": average_sentiment,
    "sentiment_absolute": sentiment_absolute,
    "sentiment_relative": sentiment_relative,
    "social_impact_score": social_impact_score,
    "galaxy_score": galaxy_score,
    "social_contributors": social_contributors,
    "social_volume_calc_24h": social_volume_calc_24h,
    "social_score_calc_24h": social_score_calc_24h,
}

filename = f"{OUTPUT_FOLDER}/social-score/social-score.json"
set_contents(filename, data, remove_old=True)
print(f"Generated output and saved in {filename}", data)
