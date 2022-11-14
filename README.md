<img src="/icon.svg" alt="Nimiq Stats Logo" />

This repository contains the auto-generated sources that we use in [nimiq.com](https://nimiq.com).

We are using [Github Actions](.github/workflows/) It will run every Monday, Thursday and Saturday at 03:00 UTC.


## Requirements

You should have the following environmental variables:

- `GITHUB_TOKEN`: Read [docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
- `TWITTER_TOKEN`: Read [docs](https://github.com/onmax/happy-tweet#twitter-bearer-token).
- `LUNARCRUSH_TOKEN`: Read [docs](https://lunarcrush.com/developers/api/authentication).

## What is it being generated?

### Tweets

We like to know what the community is saying about Nimiq. 

- [tweets.py](./src/tweets.py)
- [Tweets job](.github/workflows/fetch-data.yml#12)

#### GitHub Action

- [Tweets job](.github/workflows/fetch-data.yml#12)

#### How do we do it?

We use [Twitter's API](https://developer.twitter.com/en/docs/twitter-api/tweets/search/introduction) to get the latest tweets that contain the word `nimiq`.

Then, we filter the tweets using [finiteautomata/bertweet-base-sentiment-analysis](https://huggingface.co/finiteautomata/bertweet-base-sentiment-analysis) model from Hugging Face 🤗.

#### Output

We store two tweets datasets: [All tweets](./output/tweets/tweets.json) and [Positive tweets](./output/tweets/positive-tweets.json).

### GitHub Stats

Compute the amount of commits and additions made in the last `N_WEEKS`.

- [stats.py](./src/stats.py)
- [Stats job](.github/workflows/fetch-data.yml#38)

#### How do we do it?

We use [GitHub's statistics API](https://docs.github.com/en/rest/metrics/statistics) to get the stats of the last year, and then we filter the data to get the stats of the last `N_WEEKS`.

#### Output

We store two files: [Stats](./output/stats/stats.json) and [Stats by repo](./output/stats/stats-by-repo.json).

### Social score by LunarCrush

Fetchs social stats from [LunarCrush](https://lunarcrush.com/).

- [social_score.py](./src/social_score.py)
- [Social score job](.github/workflows/fetch-data.yml#61)

#### How do we do it?

We use [Lunarcrush's API](https://lunarcrush.com/developers/api/coins/:coin) to get the stats of NIM. These are the stats we are using:

- `social_score`:  Sum of followers, retweets, likes, reddit karma... of social posts collected
- `social_score_24h_rank`: Position/rank of the output 24 hour social score relative to all other supported output, lower is best/highest social score
- `average_sentiment`: Average sentiment of collected social posts
- `sentiment_absolute`: Percent of bullish or very bullish tweets
- `sentiment_relative`: Percent tweets that are bullish (excluding neutral in the count)
- `social_impact_score`: A proprietary score based on the relative trend of social_score
- `galaxy_score`: A proprietary score based on technical indicators of price, average social sentiment, relative social activity
- `social_contributors`: The number of unique accounts posting on social
- `social_volume_calc_24h`: Number of social posts over the last 24 hours
- `social_score_calc_24h`: Sum of social engagement over the last 24 hours

#### Output

We store the stats in [social-score.json](./output/social-score/social-score.json).

