# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:44:07 2019

@author: PAbers
"""
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

setup_url = "https://finance.yahoo.com/quote/BBY/key-statistics?p=BBY"
page = urllib.request.urlopen(setup_url)
soup = BeautifulSoup(page, 'lxml')
columns = ['Ticker']
qsp_data_table = soup.find_all('table', {'class':"table-qsp-stats"})
for table in qsp_data_table:
    for row in table.findAll("tr"):
        cells = row.findAll('td')
        columns.append(str(cells[0].find(text=True)))
df = pd.DataFrame(columns=columns)
df.set_index('Ticker', inplace=True)
tickers = ['GE', 'BBY', 'SPLK']
i = 0
for stock_symbol in tickers:
    base_url = "https://finance.yahoo.com/quote/"
    stock_specific_url = stock_symbol + "/key-statistics?p=" + stock_symbol
    whole_url = base_url+stock_specific_url
    page = urllib.request.urlopen(whole_url)
    soup = BeautifulSoup(page, 'lxml')
    print(soup.title.string)
    columns = []
    data = []
    qsp_data_table = soup.find_all('table', {'class':"table-qsp-stats"})
    for table in qsp_data_table:
        for row in table.findAll("tr"):
            cells = row.findAll('td')
            columns.append(str(cells[0].find(text=True)))
            data.append(str(cells[1].find(text=True)))
    df.loc[stock_symbol] = data
date_time_cols = [33, 34, 36, 37, 38]
for col in date_time_cols:
    df.iloc[:, col] =  pd.to_datetime(df.iloc[:, col], errors='coerce', format="%b %d, %Y")
def parse_cols(obj):
    """
    function to be applied to pandas series to convert number strings with symbols
    to floats
    """
    if obj[-1] == '%':
        obj = obj.replace('%', '')
        flt_obj = float(obj)/100
    elif obj[-1] == 'M':
        obj = obj.replace('M', '')
        flt_obj = float(obj)*10**6
    elif obj[-1] == 'B':
        obj = obj.replace('B', '')
        flt_obj = float(obj)*10**9
    elif obj == "N/A":
        flt_obj = np.nan
    else:
        flt_obj = float(obj)
    return flt_obj
for i in range(len(df.columns)):
    if i not in date_time_cols and i != 35:
        df.iloc[:, i] = df.iloc[:, i].apply(parse_cols)
        