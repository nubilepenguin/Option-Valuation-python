#
# Analyzing Euribor Interest Rate Data
# Source: http://www.emmi-benchmarks.eu/euribor-org/euribor-rates.html
# 03_stf/EURIBOR_analysis.py

import pandas as pd
from GBM_returns import *

def read_euribor_data() :
    ''' Reads historical Euribor data from Excel file, calculates
    log returns, realized variance and volatility.'''
    EBO = pd.read_excel('./EURIBOR_current.xlsx',
                        index_col=0,parse_dates=True)
    EBO['returns'] = np.log(EBO['1w']/EBO['1w'].shift(1))
    EBO = EBO.dropna()
    return EBO

data = read_euribor_data()

# Plot the Term Structure
markers = [',', '-.', '--', '-']

def plot_term_structure(data):
    ''' Plot the term structure of Euribor rates. '''
    plt.figure(figsize=(10, 5))
    for i, mat in enumerate(['1w', '1m', '6m', '12m']):
        plt.plot(data[mat].index, data[mat].values,
                 'r%s' % markers[i], label=mat)
    plt.grid()
    plt.legend()
    plt.xlabel('strike')
    plt.ylabel('implied volatility')
    plt.ylim(0.0, plt.ylim()[1])
    plt.show()

plot_term_structure(data)