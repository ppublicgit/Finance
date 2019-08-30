#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 19:43:44 2019

@author: p
"""
import numpy as np
import pandas_datareader.data as web
import statsmodels.api as sm

def hurst_ernie_chan(p):
    variancetau = []
    tau = []
    lags = range(2,100)
    for lag in lags: 
        #  Write the different lags into a vector to compute a set of tau or lags
        tau.append(lag)
        # Compute the log returns on all days, then compute the variance on the 
        # difference in log returns call this pp or the price difference
        pp = np.subtract(p[lag:], p[:-lag])
        variancetau.append(np.var(pp))
    # we now have a set of tau or lags and a corresponding set of variances.
    #print tau
    #print variancetau
    # plot the log of those variance against the log of tau and get the slope
    m = np.polyfit(np.log10(tau), np.log10(variancetau),1)
    hurst = m[0] / 2
    return hurst

def normcdf(X):  
    (a1,a2,a3,a4,a5) = (0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429)  
    L = np.abs(X)  
    K = 1.0 / (1.0 + 0.2316419 * L)  
    w = 1.0 - 1.0 / np.sqrt(2*np.pi)*np.exp(-L*L/2.) * (a1*K + a2*K*K + a3*pow(K,3) + a4*pow(K,4) + a5*pow(K,5))  
    if X < 0:  
        w = 1.0-w  
    return w

def vratio(a, lag = 2, cor = 'hom'):  
    """ the implementation found in the blog Leinenbock  
    http://www.leinenbock.com/variance-ratio-test/  
    """
    #t = (std((a[lag:]) - (a[1:-lag+1])))**2;  
    #b = (std((a[2:]) - (a[1:-1]) ))**2;  
    n = len(a)  
    mu  = sum(a[1:n]-a[:n-1])/n;  
    m=(n-lag+1)*(1-lag/n);  
    #print( mu, m, lag)  
    b=sum(np.square(a[1:n]-a[:n-1]-mu))/(n-1)  
    t=sum(np.square(a[lag:n]-a[:n-lag]-lag*mu))/m  
    vratio = t/(lag*b);
    la = float(lag)  
    if cor == 'hom':  
        varvrt=2*(2*la-1)*(la-1)/(3*la*n)  
    elif cor == 'het':  
        varvrt=0;  
        sum2=sum(np.square(a[1:n]-a[:n-1]-mu));  
        for j in range(lag-1):  
            sum1a=np.square(a[j+1:n]-a[j:n-1]-mu);  
            sum1b=np.square(a[1:n-j]-a[0:n-j-1]-mu)  
            sum1=np.dot(sum1a,sum1b);  
            delta=sum1/(sum2**2);  
            varvrt=varvrt+((2*(la-j)/la)**2)*delta  
    zscore = (vratio - 1) / np.sqrt(float(varvrt))  
    pval = normcdf(zscore);  
    return  vratio, zscore, pval

if __name__=="__main__":  
    #Revert indexes, so that indexes are in a chronological order  
    start = '2010-4-26'
    end = '2015-4-9'
    symbol1 = 'EWA'
    ps1 = web.DataReader(symbol1,'yahoo', start, end)
    ps1.rename(columns={'Adj Close':'adjclose'}, inplace=True)
    hurst = hurst_ernie_chan(ps1.adjclose)
    ps1closerev = ps1.adjclose[::-1]
    ps1closerev = np.array(ps1closerev)
    print(hurst)
    print(vratio(np.log(ps1closerev)))
    
    spread_lag = ps1.adjclose.shift(1)
    spread_lag.iloc[0] = spread_lag.iloc[1]
    spread_ret = ps1.adjclose - spread_lag
    spread_ret.iloc[0] = spread_ret.iloc[1]
    spread_lag2 = sm.add_constant(spread_lag)
    model = sm.OLS(spread_ret, spread_lag2)
    res = model.fit()
    halflife = round(-np.log(2) / res.params[1],0)
    print('Halflife = %f' %halflife)

