import numpy as np
from math import pi
from scipy.stats import truncnorm


def initialize_parameters_algorithm():  # Algorithm coefficients
    N = 30  # Number of discrete points
    delta_0=np.array([2000,2000,2000,1*340,0.5*pi,0.5*pi,0.5 *pi,100])  # Initial trust region step size
    epsilon=np.array([50,50,50,10,0.5*pi/50,0.5*pi/50,0.5*pi/50,1])   # Iteration stopping criteria
    l1 = 2
    l2 = 1.5
    l3 = 3 # Convergence coefficient
    lon0=0.0000000
    lat0=0.0000000 # Initial longitude and latitude
    cv = 1000000  # Collision avoidance chance constraint penalty coefficient
    cppc = 0.01  # Control parameter penalty coefficient
    d_safe = 50 # Safe distance
    delta_tao = 1/N  # Discretization time step
    Mpc = 1000000 # Big M penalty coefficient

    return N, delta_0, epsilon, l1, l2, l3, lon0, lat0, cv, cppc, d_safe, delta_tao, Mpc

def initialize_parameters_plane():  # Aircraft coefficients
    max_v = 3 * 340   # Maximum speed
    min_v = 0.5 * 340 # Minimum speed
    theta_max = pi/2
    theta_min = -pi/2
    psi_max = 2 * pi
    psi_min = 0
    phi_max = pi
    phi_min = -pi
    h_max = 10000  # Maximum altitude
    h_min = 1000   # Minimum altitude

    Nx_max = 1.1      # Maximum acceleration along x-axis / g
    Nx_min = -0.3     # Minimum acceleration along x-axis / g
    Nh_max = 9.0      # Maximum acceleration along z-axis / g
    Nh_min = -3.0     # Minimum acceleration along z-axis / g
    N_phi_max= 1   # Maximum roll angle rate
    N_phi_min= -1 # Minimum roll angle rate

    return max_v, min_v, theta_max, theta_min, psi_max, psi_min, phi_max, phi_min, Nx_max, Nx_min, Nh_max, Nh_min, N_phi_max, N_phi_min, h_max, h_min

def initialize_parameters_place():  # Scene parameters
    pos_plane=[15000,0,2000] # Initial position
    v0 = 1 * 340  # Initial trajectory speed
    xp0=pos_plane[0]  
    yp0=pos_plane[1] 
    h0=pos_plane[2]   
    ut0=xp0/v0  # Initial trajectory total time
    pos_target = [0, 0, 1500]  # Target position

    return pos_plane, v0, xp0, yp0, h0, ut0, pos_target

def initialize_parameters_CC():  # Chance constraint parameters
    S = 50  # Number of obstacle samples
    num_obs = 2 # Number of obstacles
    eps = 0.01
    beta = 1 - eps

    return S, num_obs, eps, beta


def initialize_trajectory(N, h0, xp0, v0, ut0):
    xk = []
    uk = []
    for i in range(N + 1):  # From 0 to N
        xk.append([h0, xp0 - v0 * ut0 * i / N, 0, v0, 0, pi, 0, ut0 * i / N])
        uk.append([0, 1, 0, ut0])
    
    return xk, uk


def initialize_obstacles(S, N, num_obs, t_total):
    from tools import get_obs_traj

    O1 = np.array([8000, -1000, 0])
    RO1 = 3000
    std1 = 500

    O2 = np.array([2000,1000,2000])
    RO2 = 1500
    O2_else = np.array([0.5 * 340, 0, 0])
    std2 = 0.01

    O1_samples = O1 + np.hstack((truncated_normal(0, std1, (S, 2)), np.zeros((S, 1))))
    v_obs_psi = truncated_normal(0, std2, S)
    O2_samples = get_obs_traj(O2, O2_else, S, N, v_obs_psi, t_total)

    return O1, RO1, std1, O2, RO2, O2_else, std2, v_obs_psi, O1_samples, O2_samples

def truncated_normal(mean, std, size):
    trunc=3 # Truncation factor
    lower, upper = mean - trunc * std, mean + trunc * std
    return truncnorm(
        (lower - mean) / std, (upper - mean) / std, loc=mean, scale=std
    ).rvs(size)