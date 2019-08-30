#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 19:24:01 2019

@author: p
"""

import numpy as np
import pandas as pd
import pandas_datareader.data as web

# Using kelly formula to calculate optimal asset allocation of a portfolio based
# on E.P. Chan's books quantatative trading and algorithmic trading where he cites 
# Thorpe's 1997 paper for inspiration

# Note that the kelly leverage has flaws (such as assuming a gaussian and assuming
# future returns will mimic current returns). Consider the kelly leverage as a upper 
# bound to leverage and consider using the more common leverage of the half kelly 
# formula

# Also, make sure to update asset allocation daily to match kelly optimization based
# on returns from each day/trading period. And make sure to update the kelly leverages
# every once in a while (consider once every several months) to reflect more recent
# stock trends

def kelly_leverages(securities, start_date, end_date, risk_free_rate=0.04):
    """
    securities: set of strings of ticker symbols in portfolio
    
    start_date: datetime date
    
    end_date: datetime date
    
    risk_free rate is annualized percentage return
    
    returns the optimal leverages for the given securites in the time frame specified.
    returns as a list of tuples (security, leveragee)
    """
    historical_prices_df = {}
    returns_dict = {}
    excess_returns_dict = {}
    # Collect data for each security from yahoo finance with pandas datareader 
    # and use to calculate excess returns (daily returns - daily risk free rate)
    for sym in securities:
        try:
            symbol_prices_df = web.DataReader(sym, 'yahoo', \
                                                  start=start_date, end=end_date)
        except IOError as e:
            raise ValueError('Download failed for %s \n Error: %s' %(sym, e))
        historical_prices_df[sym] = symbol_prices_df
        returns_dict[sym] = symbol_prices_df['Adj Close'].pct_change(1)
        excess_returns_dict[sym] = (returns_dict[sym] - (risk_free_rate / 252))
    # create a dataframe for excess returns and drop first value that (which is na)
    excess_returns_df = pd.DataFrame(excess_returns_dict).dropna()
    # Calculate covariance and mean of excess returns dataframe for calculating optimal
    # leverage and allocation
    covariance = 252 * excess_returns_df.cov()
    mean = 252 * excess_returns_df.mean()
    # Calculate the Kelly-Optimal Leverages using Matrix Multiplication (from E.P. Chan
    # Algorithmic Trading equation 8.2)
    optimal_asset_allocation = np.dot(np.linalg.inv(covariance), mean)
    # return dictionary of asset and optimal leverage (including total leverage)
    return_dict = {security: optimal_leverage for security, optimal_leverage in \
            zip(excess_returns_df.columns.values.tolist(), optimal_asset_allocation)}
    total_leverage = sum(return_dict.values())
    return_dict['Total'] = total_leverage
    return return_dict

if __name__ == '__main__':
    secs = ['OIH', 'RKH', 'RTH']  #['SPY', 'GE', 'F']
    risk_free_rate = 0.04
    start = '2000-4-26'
    end = '2007-4-9'
    kelly_weights = kelly_leverages(secs, start, end, risk_free_rate)
    