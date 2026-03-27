from scipy.stats import norm
import numpy as np

def get_Ose(S, std):
    Ose = np.hstack((np.random.normal(0, std, (S, 2)), np.zeros((S, 1))))
    return Ose

def get_Ose_five(std):
    x_q = [0.4, 0.5, 0.6, 0.5, 0.5]
    y_q = [0.5, 0.5, 0.5, 0.4, 0.6]
    x = norm.ppf(x_q, loc=0, scale=std)
    y = norm.ppf(y_q, loc=0, scale=std)
    h = np.zeros(5)
    Ose = np.stack([x, y, h], axis=1)
    return Ose

def get_vop(S, std):
    quantiles = np.linspace(0.2, 0.8, S)
    # quantiles = np.linspace(0.5, 0.5, S)
    v_obs_psi = norm.ppf(quantiles, loc=0, scale=std)
    return v_obs_psi
