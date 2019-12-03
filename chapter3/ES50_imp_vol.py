#
# Black-Scholes-Merton Implied Volatilities of # Call Options on the EURO STOXX 50
# Option Quotes from 30. September 2014
# Source: www.eurexchange.com, www.stoxx.com
# 03_stf/ES50_imp_vol.py

import numpy as np
import pandas as pd
from BSM_imp_vol import call_option
import matplotlib as mpl
import  matplotlib.pyplot as plt
mpl.rcParams['font.family'] = 'serif'
import datetime
from math import floor

# pricing Data
pdate = pd.Timestamp('30-09-2014')

#
# EURO STOXX 50 index data
#
# URL of data file
es_url = 'http://www.stoxx.com/download/historical_values/hbrbcpe.txt'
# column names to be used

cols = ['Date', 'SX5P', 'SX5E', 'SXXP', 'SXXE',
        'SXXF', 'SXXA', 'DK5F', 'DKXF', 'DEL']

# reading the data with pandas
es = pd.read_csv(es_url,
                 header=None,
                 index_col=0,
                 parse_dates=True,
                 dayfirst=True,
                 skiprows=4,
                 sep=';',
                 names=cols
                 )

# deleting the helper column
del es['DEL']
S0 = es['SX5E']['30-09-2014']
r = -0.05
#
# Option Data
#
data = pd.HDFStore('./es50_option_data.h5', 'r')['data']
print(data.head())
#
# BSM Implied Volatilities
#
print(data['Date'][1])
def calculate_imp_vols(data):
    ''' Calculate all implied volatilities for the European call options
    given the tolerance level for moneyness of the option.'''
    data['Imp_Vol'] = 0.0
    tol = 0.30 # tolerance for moneyness
    for row in data.index:
        t = datetime.datetime.fromtimestamp(floor(data['Date'][row]/1e9))
        T = datetime.datetime.fromtimestamp(floor(data['Maturity'][row]/1e9))
        data.loc[row, 'Maturity'] = T
        ttm = (T - t).days / 365.
        forward = np.exp(r * ttm) * S0
        if (abs(data['Strike'][row] - forward) / forward) < tol:
            call = call_option(S0, data['Strike'][row], t, T, r, 0.2)
            #data['Imp_Vol'][row] = call.imp_vol(data['Call'][row])
            data.loc[row,'Imp_Vol'] = call.imp_vol(data.loc[row,'Call'])
    return data

# data = calculate_imp_vols(data)

#
# Graphical Output
#

markers = ['.', 'o', '^', 'v', 'x', 'D', 'd', '>', '<']
# data['Maturity'] = datetime.datetime.fromtimestamp(floor(data['Maturity']/1e11))
def plot_imp_vols(data):
    ''' Plot the implied volatilites. '''
    maturities = sorted(set(data['Maturity']))
    plt.figure(figsize=(10, 5))
    for i, mat in enumerate(maturities):
        dat = data[(data['Maturity'] == mat) & (data['Imp_Vol'] > 0)]
        plt.plot(dat['Strike'].values, dat['Imp_Vol'].values,
                 'b%s' % markers[i], label=str(mat)[:10])
    plt.grid()
    plt.legend()
    plt.xlabel('strike')
    plt.ylabel('implied volatility')
    plt.show()

# plot_imp_vols(data)