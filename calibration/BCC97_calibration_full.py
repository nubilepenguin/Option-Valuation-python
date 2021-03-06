#
# Calibration of Bakshi, Cao and Chen (1997)
# Stoch Vol Jump Model to EURO STOXX Option Quotes
# Data Source: www.eurexchange.com
# via Numerical Integration
import math
import numpy as np
np.set_printoptions(suppress=True, formatter={'all': lambda x: '%5.3f' % x})
import pandas as pd
from scipy.optimize import brute, fmin
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'serif'
from gen_frame.BCC_option_valuation import BCC_call_value
from calibration.CIR_calibration import CIR_calibration, r_list
from gen_frame.CIR_zcb_valuation import B
from calibration.H93_calibration import options


# Calibrate Short Rate Model
#
kappa_r, theta_r, sigma_r = CIR_calibration()
#
# Market Data from www.eurexchange.com
# as of 30. September 2014
#
S0 = 3225.93 # EURO STOXX 50 level
r0 = r_list[0] # initial short rate
#
# Parameters from H93 & jump calibrations
#
kappa_v, theta_v, sigma_v, rho, v0 = np.load('opt_sv.npy')
lamb, mu, delta = np.load('opt_jump.npy')
p0 = [kappa_v, theta_v, sigma_v, rho, v0, lamb, mu, delta]
#
# Calibration Functions
#
i = 0
min_MSE = 5000.0

def BCC_error_function(p0):
    ''' Error function for parameter calibration in BCC97 model via Lewis (2001) Fourier approach.
    Parameters
    ==========
    kappa_v: float
        mean-reversion factor
    theta_v: float
        long-run mean of variance
    sigma_v: float
        volatility of variance
    rho: float
        correlation between variance and stock/index level
    v0: float
        initial, instantaneous variance
    lamb: float
        jump intensity
    mu: float
        expected jump size
    delta: float
        standard deviation of jump
    Returns
    =======
    MSE: float
        mean squared error
    '''
    global i, min_MSE
    kappa_v, theta_v, sigma_v, rho, v0, lamb, mu, delta = p0
    if kappa_v < 0.0 or theta_v < 0.005 or sigma_v < 0.0 or \
            rho < -1.0 or rho > 1.0 or v0 < 0.0 or lamb < 0.0 or \
            mu < -.6 or mu > 0.0 or delta < 0.0:
        return 5000.0
    if 2 * kappa_v * theta_v < sigma_v ** 2:
        return 5000.0
    se = []
    for row, option in options.iterrows():
        model_value = BCC_call_value(S0, option['Strike'], option['T'],
                                     option['r'], kappa_v, theta_v, sigma_v,
                                     rho, v0, lamb, mu, delta)
        se.append((model_value - option['Call']) ** 2)
    MSE = sum(se) / len(se)
    min_MSE = min(min_MSE, MSE)
    if i % 25 == 0:
        print('%4d |' % i, np.array(p0), '| %7.3f | %7.3f' % (MSE, min_MSE))
    i += 1
    return MSE

def BCC_calibration_full():
    ''' Calibrates complete BCC97 model to market quotes. '''
    # local, convex minimization for all parameters
    opt = fmin(BCC_error_function, p0,
               xtol=0.000001, ftol=0.000001,
               maxiter=450, maxfun=650)
    np.save('opt_full', np.array(opt))
    return opt

def BCC_calculate_model_values(p0):
    ''' Calculates all model values given parameter vector p0. '''
    kappa_v, theta_v, sigma_v, rho, v0, lamb, mu, delta = p0
    values = []
    for row, option in options.iterrows():
        model_value = BCC_call_value(S0, option['Strike'], option['T'],
                                     option['r'], kappa_v, theta_v, sigma_v,
                                     rho, v0, lamb, mu, delta)
        values.append(model_value)
        options.loc[row, "Model"] = model_value
    return np.array(values)

p0 = BCC_calibration_full()
BCC_calculate_model_values(p0)
options.to_hdf(path_or_buf='BCC97_option_locopt.h5', key='options')





