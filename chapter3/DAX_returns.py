# Analyzing DAX Index Quotes and Returns
# Source: http://finance.yahoo.com
# 03_stf/DAX_returns.py
from GBM_returns import *
import pandas as pd
#pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import datetime

# Read Data for DAX from the Web
def read_dax_data():
    ''' Reads historical DAX data from Yahoo! Finance, calculates log returns,
     realized variance and volatility.'''
    start = datetime.datetime(2004, 9, 30)
    end = datetime.datetime(2014, 9, 30)
    #DAX = web.get_data_yahoo('%5EGDAXI', start, end)
    DAX = web.DataReader('%5EGDAXI', 'yahoo', start, end)
    DAX.rename(columns={'Adj Close': 'index'}, inplace=True)
    DAX['returns'] = np.log(DAX['index'] / DAX['index'].shift(1))
    DAX['rea_var'] = 252 * np.cumsum(DAX['returns'] ** 2) / np.arange(len(DAX))
    DAX['rea_vol'] = np.sqrt(DAX['rea_var'])
    DAX = DAX.dropna()
    return DAX

def count_jumps(data, value):
    ''' Counts the number of return jumps as defined in size by value. '''
    jumps = np.sum(np.abs(data['returns']) > value)
    return jumps

data = read_dax_data()
print(count_jumps(data, 0.05))

# quotes_returns(data)
# return_histogram(data)
# return_qqplot(data)
# realized_volatility(data)
rolling_statistics(data)
