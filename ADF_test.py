#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 19:56:44 2019

@author: p
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import pandas_datareader.data as web

start = '2006-4-26'
end = '2012-4-9'
symbol1 = 'EWA'
symbol2 = 'EWC'
symbol3 = 'IGE'
ps1 = web.DataReader(symbol1,'yahoo', start, end)
ps2 = web.DataReader(symbol2, 'yahoo', start, end)
adf1 = adfuller(ps1['Adj Close'].values)
adf1r = adfuller(ps1['Adj Close'].pct_change()[1:].values)

print('--- ADF Test for %s ---' %symbol1)
print('ADF Statistic: %f' %adf1[0])
print('p-value: %f' %adf1[1])
print('Critical Values:')
for key, value in adf1[4].items():
    print('\t%s: %.3f' %(key, value))
print('\n')
print('--- ADF Test for %s daily returns ---' %symbol1)
print('ADF Statistic: %f' %adf1r[0])
print('p-value: %f' %adf1r[1])
print('Critical Values:')
for key, value in adf1r[4].items():
    print('\t%s: %.3f' %(key, value))
    
"""
As can be seen from the ADF test results, the price series for EWA
is not stationary as the p-value is too high to be rejected (5% critical value)
which means we cannot reject our null hypothesis that the time series is stationary.
However, the daily returns for EWA have a p-value under our critical value threshold
which means we can reject the null hypothesis which leads us to believe that the daily
returns series is stationary. This is a common phenomena in finance, as stock price time
series are rarely stationary but their daily returns often times are.
"""