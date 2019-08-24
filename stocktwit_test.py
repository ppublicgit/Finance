#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:54:19 2019

@author: p
"""
import numpy as np
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class stocktwit():
    """
    class to interact with stocktwit api
    """
    def __init__(self):
        self._symbol_json = None
        self._symbols = []
        self._read_twits_list = []
        index = pd.MultiIndex(levels=[[],[]], labels=[[],[]], names=['symbol', 'datetime'])
        self._sentiment_df = pd.DataFrame(index=index, columns=['sentiment'])
        self._analyzer = SentimentIntensityAnalyzer()
        
    def _stocktwit_api_symbol(self, symbol):
        url = "https://api.stocktwits.com/api/2/streams/symbol/" + \
        symbol + ".json"
        r = requests.get(url)
        self._symbol_json = r.json()
        
    def update_sentiment_symbol(self, symbol):
        self._stocktwit_api_symbol(symbol)
        if self._symbol_json['response'] == 404:
            raise ValueError("Invalid symbol passed as argument to get symbol data")
        for msg in self._symbol_json['messages']:
            if msg['id'] not in self._read_twits_list:
                self._read_twits_list.append(msg['id'])
                self._message_parser(msg)
        return self._symbol_json['messages']
    
    def get_symbols(self):
        return self._symbols
    
    def get_sentiment_df(self):
        self._sentiment_df.sort_index(inplace=True)
        return self._sentiment_df
    
    def _message_parser(self, message):
        if message['entities']['sentiment']:
            msg_sentiment = message['entities']['sentiment']['basic']
        else:
            msg_sentiment = self._parse_msg_sentiment(message['body'])
        if msg_sentiment == 'Bullish':
            sent_score = 1
        elif msg_sentiment == 'Bearish':
            sent_score = -1
        else:
            sent_score = msg_sentiment
        user_info = message['user']
        weight = self._parse_user_info(user_info)
        msg_time = message['created_at'][0:10]
        for syms in message['symbols']:
            if not self._sentiment_df.index.isin([(syms['symbol'], msg_time)]).any():
                self._symbols.append(syms['symbol'])
                self._sentiment_df.loc[(syms['symbol'], msg_time), :] = 0
            self._sentiment_df.loc[(syms['symbol'], msg_time), :] += sent_score*weight
            
    def _parse_msg_sentiment(self, message_data):
        vs = self._analyzer.polarity_scores(message_data)
        if vs['compound'] > 0.5:
            return vs['compound']
        elif vs['compound'] < -0.5:
            return vs['compound']
        else:
            return 0
        
    def _parse_user_info(self, user_data):
        followers_weight = self._followers_weight(user_data['followers'])
        following_weight = self._following_weight(user_data['following'])
        ideas_weight = self._ideas_weight(user_data['ideas'])
        likes_weight = self._likes_weight(user_data['like_count'])
        official_weight = self._official_weight(user_data['official'])
        total_weight = np.sum(followers_weight+following_weight+ideas_weight+ \
                    likes_weight+official_weight)
        return total_weight/10
    
    def _followers_weight(self, num_followers):
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
    
    def _following_weight(self, num_following):
        if num_following < 0:
            weight = 0
        elif num_following < 50:
            weight = 0.2
        elif num_following < 100:
            weight = 0.4
        elif num_following < 500:
            weight = 0.6
        elif num_following < 1000:
            weight = 0.8
        else:
            weight = 1.0
        return weight
    
    def _ideas_weight(self, num_ideas):
        if num_ideas < 0:
            weight = 0
        elif num_ideas < 50:
            weight = 0.2
        elif num_ideas < 100:
            weight = 0.4
        elif num_ideas < 500:
            weight = 0.6
        elif num_ideas < 1000:
            weight = 0.8
        else:
            weight = 1.0
        return weight*2
    
    def _likes_weight(self, num_likes):
        if num_likes < 0:
            weight = 0
        elif num_likes < 50:
            weight = 0.2
        elif num_likes < 100:
            weight = 0.4
        elif num_likes < 500:
            weight = 0.6
        elif num_likes < 1000:
            weight = 0.8
        else:
            weight = 1.0
        return weight
    
    def _official_weight(self, off_bool):
        weight = 3
        return weight*float(off_bool)

if __name__ ==  "__main__":
    stw = stocktwit()
    symbols = ["AAPL", "SPY", "GE", "CRM"]
    for symb in symbols:
        a = stw.update_sentiment_symbol(symb)
    b = stw.get_symbols()
    c = stw.get_sentiment_df()