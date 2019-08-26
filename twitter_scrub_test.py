#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 10:24:32 2019

@author: p
"""
import numpy as np
import pandas as pd
import tweepy
from datetime import datetime
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class twitter_scrubber():
    
    def __init__(self):
        self._twitter_api_tokens_df = pd.read_csv('Twitter_API_df_tokens.csv', index_col=0)
        self._api = None
        username_index = pd.MultiIndex(levels=[[],[], []], labels=[[],[], []], \
                                       names=['username', 'created_at', 'tweet_id'])
        self._user_tweets_df = pd.DataFrame(index=username_index, \
                                            columns=['tweet'])
        search_index = pd.MultiIndex(levels=[[],[], []], labels=[[],[], []], \
                                     names=['symbol', 'created_at', 'tweet_id'])
        self._user_tweets_df = pd.DataFrame(index=search_index, \
                                            columns=['tweet', 'username'])
        sentiment_index = pd.MultiIndex(levels=[[],[]], labels=[[],[]], \
                                     names=['symbol', 'date'])
        self._sentiment_tweets_df = pd.DataFrame(index=sentiment_index, \
                                                 columns = ['Total_User_Weights', 'Total_Tweet_Weights', \
                                                            'Bullish_Count', 'Bearish_Count', \
                                                            'Neutral_Count', 'Total_Count', \
                                                            'Unweighted_Sentiment', 'Total_Sentiment'])
        self._analyzer = SentimentIntensityAnalyzer()
        
    def set_api_app_keys(self, twitter_api_app):
        """
        Set access keys and tokens to use the api app specified in call to method
        """
        CONSUMER_KEY = self._twitter_api_tokens_df.loc[twitter_api_app, 'CONSUMER_KEY']
        CONSUMER_SECRET = self._twitter_api_tokens_df.loc[twitter_api_app, 'CONSUMER_SECRET']
        ACCESS_TOKEN = self._twitter_api_tokens_df.loc[twitter_api_app, 'ACCESS_KEY']
        ACCESS_TOKEN_SECRET = self._twitter_api_tokens_df.loc[twitter_api_app, 'ACCESS_SECRET']
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self._api = tweepy.API(auth)
    
    def _limit_handled(self, cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                time.sleep(2)
    
    def update_tweets_username(self, username, count):
        ct = 0
        for tweet in self._limit_handled(tweepy.Cursor(self._api.user_timeline, id=username).items()):
            if tweet.text.startswith('RT'):
                continue
            # Remove replies
            elif tweet.text.startswith('@'):
                continue
            else:    
                self._user_tweets_df.loc[(username, tweet.created_at, tweet.id_str), 'tweet'] = tweet.text
                ct += 1
                if ct == count:
                    break
    
    def update_tweets_symbol(self, symbol, date_since, count):
        no_rt_keyword = "$" + symbol + " -filter:retweets"
        new_tweets = self._limit_handled(tweepy.Cursor(self._api.search,
              q=no_rt_keyword,
              lang="en",
              since=date_since).items(count))
        outtweets = [[tweet.id_str, tweet.created_at, \
                      tweet.text, tweet.user.screen_name, \
                      tweet.retweet_count, tweet.favorite_count] for tweet in new_tweets]
        for tweet in outtweets:
            self._user_tweets_df.loc[(symbol, tweet[1], tweet[0]), ['tweet', 'username']] = tweet[2], tweet[3]
            if not self._sentiment_tweets_df.index.isin([(symbol, str(tweet[1].date()))]).any():
                self._sentiment_tweets_df.loc[(symbol, str(tweet[1].date())), :] = 0
            self._sentiment_analyis_tweet(symbol, tweet)

    def get_tweets_username(self, username):
        return self._user_tweets_df.loc[[username], 'tweet']
    
    def get_tweets_symbol(self, symbols):
        return self._user_tweets_df.loc[symbols, :]
    
    def get_all_sentiments(self):
        return self._sentiment_tweets_df
    
    def get_symbol_sentiments(self, symbol):
        return self._sentiment_tweets_df.xs(symbol)
    
    def _sentiment_analyis_tweet(self, symbol, tweet):
        date = str(tweet[1].date())
        tweet_text = tweet[2]
        screenname = tweet[3]
        num_retweets = tweet[4]
        num_likes = tweet[5]
        sent_score, sentiment = self._parse_tweet(tweet_text)
        user_weights = self._calc_user_weight(screenname)
        tweet_weights = self._calc_tweet_weight(num_retweets, num_likes)
        total_weight = user_weights+tweet_weights
        self._sentiment_tweets_df.loc[(symbol, date), \
                                      ['Total_User_Weights', 'Total_Tweet_Weights', \
                                       sentiment, "Total_Count", \
                                       'Unweighted_Sentiment', 'Total_Sentiment']] += [user_weights, tweet_weights, \
                                       1, 1, sent_score, sent_score*total_weight]
        
    def _calc_tweet_weight(self, num_rt, num_lks):
        retweet_wt = self._calc_retweets_weight(num_rt)
        likes_wt = self._calc_likes_weight(num_lks)
        tweet_wts = retweet_wt+likes_wt
        return tweet_wts/10
    
    def _calc_user_weight(self, username):
        user_info = self._api.get_user(id=username)
        followers_wt = self._calc_followers_weight(user_info.followers_count)
        friends_wt = self._calc_friends_weight(user_info.friends_count)
        favourites_wt = self._calc_favourites_weight(user_info.favourites_count)
        verified_wt = self._calc_verified_weight(user_info.verified)
        statuses_wt = self._calc_statuses_weight(user_info.statuses_count)
        user_wts = followers_wt+friends_wt+favourites_wt+verified_wt+statuses_wt
        return user_wts/10
    
    def _parse_tweet(self, tweet):
        vs = self._analyzer.polarity_scores(tweet)
        if vs['compound'] > 0.5:
            return vs['compound'], 'Bullish_Count'
        elif vs['compound'] < -0.5:
            return vs['compound'], 'Bearish_Count'
        else:
            return 0, "Neutral_Count"
        
    def _calc_followers_weight(self, num_followers):
        if num_followers < 0:
            weight = 0
        elif num_followers < 100:
            weight = 0.2
        elif num_followers < 500:
            weight = 0.4
        elif num_followers < 2000:
            weight = 0.6
        elif num_followers < 10000:
            weight = 0.8
        else:
            weight = 1.0
        return weight*3
    
    def _calc_friends_weight(self, num_friends):
        if num_friends < 0:
            weight = 0
        elif num_friends < 50:
            weight = 0.2
        elif num_friends < 100:
            weight = 0.4
        elif num_friends < 500:
            weight = 0.6
        elif num_friends < 1000:
            weight = 0.8
        else:
            weight = 1.0
        return weight
    
    def _calc_statuses_weight(self, num_statuses):
        if num_statuses < 0:
            weight = 0
        elif num_statuses < 50:
            weight = 0.2
        elif num_statuses < 100:
            weight = 0.4
        elif num_statuses < 500:
            weight = 0.6
        elif num_statuses < 1000:
            weight = 0.8
        else:
            weight = 1.0
        return weight*2
    
    def _calc_favourites_weight(self, num_favourites):
        if num_favourites < 0:
            weight = 0
        elif num_favourites < 50:
            weight = 0.2
        elif num_favourites < 100:
            weight = 0.4
        elif num_favourites < 500:
            weight = 0.6
        elif num_favourites < 1000:
            weight = 0.8
        else:
            weight = 1.0
        return weight
    
    def _calc_verified_weight(self, verified_bool):
        weight = 3*float(verified_bool)
        return weight
    
    def _calc_retweets_weight(self, num_retweets):
        if num_retweets < 0:
            weight = 0
        elif num_retweets < 100:
            weight = 0.2
        elif num_retweets < 500:
            weight = 0.4
        elif num_retweets < 2000:
            weight = 0.6
        elif num_retweets < 10000:
            weight = 0.8
        else:
            weight = 1.0
        return weight*5
    
    def _calc_likes_weight(self, num_likes):
        if num_likes < 0:
            weight = 0
        elif num_likes < 100:
            weight = 0.2
        elif num_likes < 500:
            weight = 0.4
        elif num_likes < 2000:
            weight = 0.6
        elif num_likes < 10000:
            weight = 0.8
        else:
            weight = 1.0
        return weight*5
    
if __name__ == '__main__':
    tws = twitter_scrubber()
    tws.set_api_app_keys('tweepy_test')
    tws.update_tweets_username('@realDonaldTrump', 10)
    username_tweets = tws.get_tweets_username('@realDonaldTrump')
    symbols = ["AAPL", "GE", "FB"]
    date_from = "2019-08-20"
    for symb in symbols:
        tws.update_tweets_symbol(symb, date_from, 10)
    symbol_tweets = tws.get_tweets_symbol(symbols)
    all_sentiment = tws.get_all_sentiments()
    ge_sentiment = tws.get_symbol_sentiments("GE")
    aapl_sentiment = tws.get_symbol_sentiments("AAPL")
        