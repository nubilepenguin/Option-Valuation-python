#
# Valuation of European Call Options
# in Merton's (1976) Jump Diffusion Model
# via Fast Fourier Transform (FFT)

import math
import numpy as np
from numpy.fft import *

#
# Model Parameters
#
S0 = 100.0 # initial index level
K = 100.0 # strike level
T = 1.0 # call option maturity
r = 0.05 # constant short rate
sigma = 0.4 # constant volatility of diffusion
lamb = 1.0 # jump frequency p.a.
mu = - 0.2 # expected jump size
delta = 0.1 # jump size volatility

def M76_characteristic_function(u, x0, T, r, sigma, lamb, mu, delta):
    ''' Valuation of European call option in M76 model via
    Lewis (2001) Fourier-based approach: characteristic function.

    Parameter definitions see function M76_value_call_FFT. '''
    omega = x0 / T + r - 0.5 * sigma ** 2 - lamb * (np.exp(mu + 0.5 * delta ** 2) - 1)
    value = (1j * u * omega - 0.5 * u ** 2 * sigma ** 2 + \
             lamb * (np.exp(1j * u * mu - 0.5 * u ** 2 * delta ** 2) - 1)) * T
    return np.exp(value)

#
# Valuation by FFT
#

def M76_value_call_FFT(S0, K, T, r, sigma, lamb, mu, delta):
    ''' Valuation of European call option in M76 model via
    Carr-Madan(1999) Fourier-based approach.

    Parameters
    ==========
    S0: float
            initial stock/index level
    K: float
            strike price
    T: float
        time-to-maturity(for t=0)
    r: float
        constant risk-free short rate
    sigma: float
        volatility factor in diffusion term
    lamb: float
        jump intensity
    mu: float
        expected jump size
    delta: float
        standard deviation of jump

    Returns

    =======
    call_value: float
        European call option present value
    '''

    k = math.log(K / S0)
    x0 = math.log(S0 / S0)
    g = 2 # factor to increase accuracy
    N = g * 4096
    eps = (g * 150.) ** -1
    eta = 2 * math.pi / (N * eps)
    b = 0.5 * N * eps - k
    u = np.arange(1, N + 1, 1)
    vo = eta * (u - 1)
    # Modificatons to Ensure Integrability
    if S0 >= 0.95 * K : #ITM
        alpha = 1.5
        v = vo - (alpha + 1) * 1j
        modcharFunc = np.exp(-r * T) * (M76_characteristic_function(
            v, x0, T, r, sigma, lamb, mu, delta) / (alpha ** 2 + alpha - vo ** 2 + 1j * (2 * alpha + 1) * vo))
    else:
        alpha = 1.1
        v = (vo - 1j * alpha) - 1j
        modcharFunc1 = np.exp(-r * T) * (1 / (1 + 1j * (vo - 1j * alpha))
                                         - np.exp(r * T)/(1j * (vo - 1j * alpha))
                                         - M76_characteristic_function(v,x0,T,r,sigma,lamb, mu, delta)/
                                         ((vo - 1j * alpha) ** 2 - 1j * (vo - 1j * alpha)))
        v = (vo + 1j * alpha) - 1j
        modcharFunc2 = np.exp(-r * T) * (1 / (1 + 1j * (vo + 1j * alpha))
                                         - np.exp(r * T)/ (1j * (vo + 1j * alpha))
                                         - M76_characteristic_function(v, x0, T, r, sigma, lamb, mu, delta) /
                                         ((vo + 1j * alpha) ** 2 - 1j * (vo + 1j * alpha)))

    # Numerical FFT Routine
    delt = np.zeros(N, dtype=np.float)
    delt[0] = 1
    j = np.arange(1, N + 1, 1)

    SimpsonW = (3 + (-1) ** j - delt) / 3
    if S0 >= 0.95 * K:
        FFTFunc = np.exp(1j * b * vo) * modcharFunc * eta * SimpsonW
        payoff = (fft(FFTFunc)).real
        CallValueM = np.exp(-alpha * k) / np.pi * payoff
    else:
        FFTFunc = (np.exp(1j * b * vo) * (modcharFunc1 - modcharFunc2) * 0.5 * eta * SimpsonW)
        payoff = (fft(FFTFunc)).real
        CallValueM = payoff / (np.sinh(alpha * k) * np.pi)
    pos = int((k + b) / eps)
    CallValue = CallValueM[pos] * S0
    # klist = np.exp((np.arange(0, N, 1) - 1) * eps - b) * S0
    return CallValue  # , klist[pos - 50:pos + 50]

if __name__ == '__main__':
    print ("Value of Call Option %8.3f" \
        % M76_value_call_FFT(S0, K, T, r, sigma, lamb, mu, delta))