# Sources for nimiq.com

This repository contains the auto-generated sources that we use in [nimiq.com](https://nimiq.com).

We are using [Github Actions](.github/workflows/) It will run every Monday, Thursday and Saturday at 03:00 UTC.

## What is it being generated?

### Tweets

We like to know what the community is saying about Nimiq. 

#### Code

- [tweets.py](./src/tweets.py)


#### How do we do it?

We use [Twitter's API](https://developer.twitter.com/en/docs/twitter-api/tweets/search/introduction) to get the latest tweets that contain the word `nimiq`.

Then, we filter the tweets using [finiteautomata/bertweet-base-sentiment-analysis](https://huggingface.co/finiteautomata/bertweet-base-sentiment-analysis) model from Hugging Face 🤗.

#### Output

We store two tweets datasets: [All tweets](./assets/tweets/tweets.json) and [Positive tweets](./assets/tweets/positive-tweets.json).
