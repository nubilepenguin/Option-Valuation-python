import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'serif'
from data.BSM_imp_vol import call_option
from gen_frame.CIR_zcb_valuation import B
from calibration.H93_calibration import S0, r0, kappa_r, theta_r, sigma_r

#
# Calibration Results
#

def calculate_implied_volatilities(filename):
    ''' Calculates market and model implied volatilities. '''
    h5 = pd.HDFStore(filename, 'r')
    options = h5['options']
    h5.close()
    tol = 0.02  # percent ITM/OTM options
    # options = data[(np.abs(data['Strike'] - S0)) / S0 < tol]
    # options['Date'] = pd.DatetimeIndex(options['Date'])
    # options['Maturity'] = pd.DatetimeIndex(options['Maturity'])
    # options['Date'] = pd.DatetimeIndex(options['Date'])
    # options['Maturity'] = pd.DatetimeIndex(options['Maturity'])
    for row, option in options.iterrows():
        T = (option['Maturity'] - option['Date']).days / 365.
        BOT = B([kappa_r, theta_r, sigma_r, r0, T])
        r = -math.log(BOT) / T
        call = call_option(S0, option['Strike'], option['Date'],
                           option['Maturity'], option['r'], 0.1)
        options.loc[row, 'market_iv'] = call.imp_vol(option['Call'], 0.15)
        options.loc[row, 'model_iv'] = call.imp_vol(option['Model'], 0.15)
    return options

def plot_implied_volatilities(options, model):
    ''' Plots market implied volatilities against model implied ones. '''
    mats = sorted(set(options.Maturity))
    for mat in mats:
        opts = options[options.Maturity == mat]
        plt.figure(figsize=(8, 6))
        plt.subplot(211)
        plt.ylabel('implied volatility')
        plt.plot(opts.Strike, opts.market_iv, 'b', label='market', lw=1.5)
        plt.plot(opts.Strike, opts.model_iv, 'ro', label='model')
        plt.legend(loc=0)
        plt.axis([min(opts.Strike) - 10, max(opts.Strike) + 10,
                  min(opts.market_iv) - 0.015, max(opts.market_iv) + 0.015])
        plt.title('Maturity %s' % str(mat)[:10])
        plt.subplot(212)
        wi = 5.0
        diffs = opts.model_iv.values - opts.market_iv.values
        plt.bar(opts.Strike.values - wi / 2, diffs, width=wi)
        plt.ylabel('difference')
        ymi = min(diffs) - (max(diffs) - min(diffs)) * 0.1
        yma = max(diffs) + (max(diffs) - min(diffs)) * 0.1
        plt.axis([min(opts.Strike) - 10, max(opts.Strike) + 10, ymi, yma])
        plt.tight_layout()
        plt.savefig('./%s_calibration_iv_%s.pdf'
                    % (model, str(mat)[:10]))


filename = 'demo.h5'
options = calculate_implied_volatilities(filename)
plot_implied_volatilities(options, model='H93')



