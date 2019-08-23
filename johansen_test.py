#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 20:25:34 2019

@author: p
"""

"""
Exercise is from Algorithmic Trading  by E.P. Chan
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from johansen import coint_johansen
"""
johansen test has a null hypothesis that time series are not cointegrated.
"""

start = '2006-4-26'
end = '2012-4-9'
symbol1 = 'EWA'
symbol2 = 'EWC'
symbol3 = 'IGE'
ps1 = web.DataReader(symbol1,'yahoo', start, end)
ps2 = web.DataReader(symbol2, 'yahoo', start, end)

plt.figure()
plt.plot(ps1.index, ps1['Adj Close'].values, 'r')
plt.plot(ps2.index, ps2['Adj Close'].values, 'b')
plt.legend(['EWA','EWC'])
plt.show()
ps3 = web.DataReader(symbol3, 'yahoo', start, end)


df = pd.DataFrame( {symbol1:ps1['Adj Close'] , symbol2:ps2['Adj Close'], symbol3:ps3['Adj Close']}, \
                    index=ps1.index )

print(coint_johansen(df, 0, 1))