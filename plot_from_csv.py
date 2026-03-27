from ininital import initialize_parameters_algorithm, initialize_parameters_plane, initialize_parameters_place, initialize_parameters_CC, initialize_trajectory, initialize_obstacles
from output_info import organize_xk, organize_uk, get_vio_percentage, create_acmi
from plot_picture import plot_trajectory, plot_results
import pandas as pd
import os
import glob


def load_data_from_csv():
    """Reconstruct xk_all and uk_all from CSV files in the result folder"""
    result_dir = "result"
    
    # Get all CSV files for x and u
    x_files = sorted(glob.glob(os.path.join(result_dir, "output_x_*.csv")))
    u_files = sorted(glob.glob(os.path.join(result_dir, "output_u_*.csv")))
    
    xk_all = []
    uk_all = []
    
    # Sort by file number (extract numeric part for sorting)
    x_files.sort(key=lambda x: int(os.path.basename(x).split('_')[2].split('.')[0]))
    u_files.sort(key=lambda x: int(os.path.basename(x).split('_')[2].split('.')[0]))
    
    # print(f"Found {len(x_files)} x files and {len(u_files)} u files")
    
    for x_file, u_file in zip(x_files, u_files):
        # print(f"Loading {os.path.basename(x_file)} and {os.path.basename(u_file)}")
        
        # Read x data
        x_df = pd.read_csv(x_file)
        # Reorder columns to match xk format: [hp, xp, yp, v, theta, psi, phi, tp]
        xk_iter = []
        for _, row in x_df.iterrows():
            xk_iter.append([row['hp'], row['xp'], row['yp'], row['v'], 
                          row['theta'], row['psi'], row['phi'], row['tp']])
        xk_all.append(xk_iter)
        
        # Read u data
        u_df = pd.read_csv(u_file)
        # uk format: [Nx, Nh, N_phi, t_total]
        uk_iter = []
        for _, row in u_df.iterrows():
            uk_iter.append([row['Nx'], row['Nh'], row['N_phi'], row['t_total']])
        uk_all.append(uk_iter)
    
    return xk_all, uk_all


N, delta_0, epsilon, l1, l2, l3, lon0, lat0, cv, cppc, d_safe, delta_tao, Mpc = initialize_parameters_algorithm()
max_v, min_v, theta_max, theta_min, psi_max, psi_min, phi_max, phi_min, Nx_max, Nx_min, Nh_max, Nh_min, N_phi_max, N_phi_min, h_max, h_min = initialize_parameters_plane()
pos_plane, v0, xp0, yp0, h0, ut0, pos_target = initialize_parameters_place()
S, num_obs, eps, beta = initialize_parameters_CC()
xk,uk = initialize_trajectory(N, h0, xp0, v0, ut0)
O1, RO1, std1, O2, RO2, O2_else, std2, v_obs_psi, O1_samples, O2_samples = initialize_obstacles(S, N, num_obs, uk[-1][-1])

# Load data from CSV files
xk_all, uk_all = load_data_from_csv()
iter = len(xk_all) - 1  # Number of iterations should be data length minus 1

# print(f"Loaded {len(xk_all)} iterations of data")
# print(f"Each iteration has {len(xk_all[0])} time steps")

xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all = organize_xk(N, xk_all)
Nx_all, Nh_all, N_phi_all, t_total_all = organize_uk(N, uk_all)
# get_vio_percentage(xk_all[-1], N, O1, O2, O2_else, RO1, RO2, std1, std2, t_total_all[-1][-1])
create_acmi(xk_all[-1], uk_all[-1], N, O1_samples, O2_samples)

# plot_trajectory(N, iter, xp_all, yp_all, hp_all, O1_samples, RO1, O2_samples, RO2)
# plot_results(N, iter, xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all, Nx_all, Nh_all, N_phi_all, t_total_all)
