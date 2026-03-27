import gurobipy as gp
from gurobipy import GRB
import numpy as np
from math import e
import time


from ininital import initialize_parameters_algorithm, initialize_parameters_plane, initialize_parameters_place, initialize_parameters_CC, initialize_trajectory, initialize_obstacles
from tools import HWGc,nabla_pS,get_obs_traj
from plot_picture import plot_trajectory, plot_results
from output_info import organize_xk, organize_uk, create_acmi, get_vio_percentage
from tools_deter import get_Ose_five, get_vop
import pandas as pd


def initial_traj(iter_initial):
    begin_time = time.time()
    # Initialization
    # xk = [hp, xp, yp, v, theta, psi, phi, tp], uk = [Nx, Nh, N_phi, t_total]
    N, delta_0, epsilon, l1, l2, l3, lon0, lat0, cv, cppc, d_safe, delta_tao, Mpc = initialize_parameters_algorithm()
    max_v, min_v, theta_max, theta_min, psi_max, psi_min, phi_max, phi_min, Nx_max, Nx_min, Nh_max, Nh_min, N_phi_max, N_phi_min, h_max, h_min = initialize_parameters_plane()
    pos_plane, v0, xp0, yp0, h0, ut0, pos_target = initialize_parameters_place()
    S, num_obs, eps, beta = initialize_parameters_CC()
    xk,uk = initialize_trajectory(N, h0, xp0, v0, ut0)
    O1, RO1, std1, O2, RO2, O2_else, std2, v_obs_psi, O1_samples, O2_samples = initialize_obstacles(S, N, num_obs, uk[-1][-1])

    # Read uk.csv and xk.csv
    # uk = pd.read_csv("uk.csv", header=None).values.tolist()
    # xk = pd.read_csv("xk.csv", header=None).values.tolist()

    # Record values of xk, uk at all times
    xk_all = [xk]
    uk_all = [uk]


    # Main changes
    S = 5
    O1_samples = O1 + get_Ose_five(std1)
    v_obs_psi = get_vop(S, std2)
    O2_samples = get_obs_traj(O2, O2_else, S, N, v_obs_psi, uk[-1][-1])

    # Deterministic method
    S = 1
    O1_samples = [O1]
    v_obs_psi = [0]
    O2_samples = get_obs_traj(O2, O2_else, S, N, v_obs_psi, uk[-1][-1])


    # ----------------------------
    # Create model
    # ----------------------------
    model = gp.Model("AircraftTrajectoryOptimization")

    model.setParam("OutputFlag", 0)   # Whether to print output
    model.setParam("Threads", 4)      # Number of threads
    model.setParam("Presolve", 2)     # Presolve level
    model.setParam("Heuristics", 0.5) # Heuristic search ratio
    model.setParam("Cuts", 2)         # Cutting plane strength
    model.setParam('TimeLimit', 600)   # Set solving time limit (unit: seconds)

    # ----------------------------
    # Add variables
    # ----------------------------

    # Continuous variables
    Nx = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="Nx")
    Nh = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="Nh")
    N_phi = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="N_phi")
    t_total = model.addVar(vtype=GRB.CONTINUOUS, name="t_total")
    xp = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="xp")
    yp = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="yp")
    hp = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="hp")
    v = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="v")
    theta = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="theta")
    psi = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="psi")
    phi = model.addVars(N + 1, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="phi")
    tp = model.addVars(N + 1, vtype=GRB.CONTINUOUS, name="time")
    x_det = model.addVars(N+1, 8, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="x")
    u_det = model.addVars(N+1, 4, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="u")

    # Slack variables
    slack = model.addVars(N, S, vtype=GRB.CONTINUOUS, name="slack")

    # Auxiliary variables for absolute values of control parameters
    abs_Nx = model.addVars(N+1, vtype=GRB.CONTINUOUS, name="abs_Nx")
    abs_Nh = model.addVars(N+1, vtype=GRB.CONTINUOUS, name="abs_Nh")
    abs_N_phi = model.addVars(N+1, vtype=GRB.CONTINUOUS, name="abs_N_phi")
    abs_phi = model.addVars(N+1, vtype=GRB.CONTINUOUS, name="abs_phi")


    # ----------------------------
    # Add constraints
    # ----------------------------

    # Safety constraints
    for i in range(N + 1):
        model.addConstr(Nx[i] >= Nx_min, name=f"Nx_min_{i}")
        model.addConstr(Nx[i] <= Nx_max, name=f"Nx_max_{i}")
        model.addConstr(Nh[i] >= Nh_min, name=f"Nh_min_{i}")
        model.addConstr(Nh[i] <= Nh_max, name=f"Nh_max_{i}")
        model.addConstr(N_phi[i] >= N_phi_min, name=f"N_phi_min_{i}")
        model.addConstr(N_phi[i] <= N_phi_max, name=f"N_phi_max_{i}")
        model.addConstr(hp[i] >= h_min, name=f"hp_min_{i}")
        model.addConstr(hp[i] <= h_max, name=f"hp_max_{i}")
        model.addConstr(v[i] >= min_v, name=f"v_min_{i}")
        model.addConstr(v[i] <= max_v, name=f"v_max_{i}")
        model.addConstr(theta[i] >= theta_min, name=f"theta_min_{i}")
        model.addConstr(theta[i] <= theta_max, name=f"theta_max_{i}")
        model.addConstr(psi[i] >= psi_min, name=f"psi_min_{i}")
        model.addConstr(psi[i] <= psi_max, name=f"psi_max_{i}")
        model.addConstr(phi[i] >= phi_min, name=f"phi_min_{i}")
        model.addConstr(phi[i] <= phi_max, name=f"phi_max_{i}")

    # Trust-region constraints
    delta = delta_0
    for i in range(N + 1):
        model.addConstr(hp[i] <= xk[i][0] + delta[0], name=f"hp_trust_{i}")
        model.addConstr(hp[i] >= xk[i][0] - delta[0], name=f"hp_trust_{i}_neg")
        model.addConstr(xp[i] <= xk[i][1] + delta[1], name=f"xp_trust_{i}")
        model.addConstr(xp[i] >= xk[i][1] - delta[1], name=f"xp_trust_{i}_neg")
        model.addConstr(yp[i] <= xk[i][2] + delta[2], name=f"yp_trust_{i}")
        model.addConstr(yp[i] >= xk[i][2] - delta[2], name=f"yp_trust_{i}_neg")
        model.addConstr(v[i] <= xk[i][3] + delta[3], name=f"v_trust_{i}")
        model.addConstr(v[i] >= xk[i][3] - delta[3], name=f"v_trust_{i}_neg")
        model.addConstr(theta[i] <= xk[i][4] + delta[4], name=f"theta_trust_{i}")
        model.addConstr(theta[i] >= xk[i][4] - delta[4], name=f"theta_trust_{i}_neg")
        model.addConstr(psi[i] <= xk[i][5] + delta[5], name=f"psi_trust_{i}")
        model.addConstr(psi[i] >= xk[i][5] - delta[5], name=f"psi_trust_{i}_neg")
        model.addConstr(phi[i] <= xk[i][6] + delta[6], name=f"phi_trust_{i}")
        model.addConstr(phi[i] >= xk[i][6] - delta[6], name=f"phi_trust_{i}_neg")
        model.addConstr(tp[i] <= xk[i][7] + delta[7], name=f"tp_trust_{i}")
        model.addConstr(tp[i] >= xk[i][7] - delta[7], name=f"tp_trust_{i}_neg")

    # Initial state constraints
    model.addConstr(hp[0] == xk[0][0], name="hp_initial")
    model.addConstr(xp[0] == xk[0][1], name="xp_initial")
    model.addConstr(yp[0] == xk[0][2], name="yp_initial")
    model.addConstr(v[0] == xk[0][3], name="v_initial")
    model.addConstr(theta[0] == xk[0][4], name="theta_initial")
    model.addConstr(psi[0] == xk[0][5], name="psi_initial")
    model.addConstr(phi[0] == xk[0][6], name="phi_initial")
    model.addConstr(tp[0] == xk[0][7], name="tp_initial")

    # Motion equation constraints
    H_all, W_all, G_all, C_all = HWGc(xk, uk, delta_tao, N)  # Get linearized matrices H_all, W_all, G, C
    for i in range(1, N + 1):
        for j in range(8):
            expr = gp.LinExpr()
            for k in range(8):
                expr += float(H_all[i-1][j, k]) * x_det[i-1, k]
                expr += float(W_all[i][j, k]) * x_det[i, k]
            for k in range(4):
                expr += float(G_all[i-1][j, k]) * u_det[i-1, k]
                expr += float(G_all[i][j, k]) * u_det[i, k]
            rhs = -delta_tao / 2 * float(C_all[i-1][0,j] + C_all[i][0,j])
            model.addConstr(expr == rhs, name=f"motion_eq_{i}_{j}")

    for i in range(N + 1):  # Relationship between x, u and other variables
        model.addConstr(x_det[i, 0] == hp[i], name=f"x_det_hp_{i}")
        model.addConstr(x_det[i, 1] == xp[i], name=f"x_det_xp_{i}")
        model.addConstr(x_det[i, 2] == yp[i], name=f"x_det_yp_{i}")
        model.addConstr(x_det[i, 3] == v[i], name=f"x_det_v_{i}")
        model.addConstr(x_det[i, 4] == theta[i], name=f"x_det_theta_{i}")
        model.addConstr(x_det[i, 5] == psi[i], name=f"x_det_psi_{i}")
        model.addConstr(x_det[i, 6] == phi[i], name=f"x_det_phi_{i}")
        model.addConstr(x_det[i, 7] == tp[i], name=f"x_det_tp_{i}")

        model.addConstr(u_det[i, 0] == Nx[i], name=f"u_det_Nx_{i}")
        model.addConstr(u_det[i, 1] == Nh[i], name=f"u_det_Nh_{i}")
        model.addConstr(u_det[i, 2] == N_phi[i], name=f"u_det_N_phi_{i}")
        model.addConstr(u_det[i, 3] == t_total, name=f"u_det_t_total_{i}")


    # Terminal constraints
    model.addConstr(xp[N] == pos_target[0], name="xp_target")
    model.addConstr(yp[N] == pos_target[1], name="yp_target")
    model.addConstr(hp[N] == pos_target[2], name="hp_target")

    # Absolute-value constraints for control parameters
    for i in range(N+1):
        model.addConstr(abs_Nx[i] >= Nx[i])
        model.addConstr(abs_Nx[i] >= -Nx[i])
        model.addConstr(abs_Nh[i] >= Nh[i])
        model.addConstr(abs_Nh[i] >= -Nh[i])
        model.addConstr(abs_N_phi[i] >= N_phi[i])
        model.addConstr(abs_N_phi[i] >= -N_phi[i])
        model.addConstr(abs_phi[i] >= phi[i])
        model.addConstr(abs_phi[i] >= -phi[i])

    # Collision-avoidance constraints
    for i in range(N):
        p_i_k = [xk[i][1], xk[i][2], xk[i][0]]  # Aircraft position at current time
        for s in range(S):
            sd_obs1 = np.linalg.norm(p_i_k - O1_samples[s], 2)
            nabla = nabla_pS(p_i_k, O1_samples[s])
            expr = gp.LinExpr()
            expr += nabla[0] * (xp[i] - p_i_k[0]) + nabla[1] * (yp[i] - p_i_k[1]) + nabla[2] * (hp[i] - p_i_k[2])
            model.addConstr(slack[i,s] + expr >= RO1 - sd_obs1 + d_safe, name=f"escape_obs1_{i}_{s}")

    for i in range(N):
        p_i_k = [xk[i][1], xk[i][2], xk[i][0]]  # Aircraft position at current time
        for s in range(S):
            sd_obs2 = np.linalg.norm(p_i_k - O2_samples[s][i], 2)
            nabla = nabla_pS(p_i_k, O2_samples[s][i])
            expr = gp.LinExpr()
            expr += nabla[0] * (xp[i] - p_i_k[0]) + nabla[1] * (yp[i] - p_i_k[1]) + nabla[2] * (hp[i] - p_i_k[2])
            model.addConstr(slack[i,s] + expr >= RO2 - sd_obs2 + d_safe, name=f"escape_obs2_{i}_{s}")

    # ----------------------------
    # Set objective function
    # ----------------------------
    # Example: minimize trajectory cost and collision-avoidance penalty
    obj = t_total\
        + cv * gp.quicksum(slack[i,s] for i in range(N) for s in range(S))\
        + cppc * gp.quicksum(abs_Nx[i] + abs_Nh[i] for i in range(N+1))\
        + cppc * gp.quicksum(abs_N_phi[i] for i in range(N+1))\
        + 0.01 * gp.quicksum(abs_phi[i] for i in range(N+1))
    model.setObjective(obj, GRB.MINIMIZE)


    # ----------------------------
    # Solve model
    # ----------------------------

    iter=0
    while iter < iter_initial:
        model.optimize()
        iter += 1
        print(f"Iteration {iter}, Objective Value: {model.ObjVal}, t_total: {t_total.X}, Time: {model.Runtime:.2f} seconds")

        # Update xk and uk
        xk = [[hp[i].X, xp[i].X, yp[i].X, v[i].X, theta[i].X, psi[i].X, phi[i].X, tp[i].X] for i in range(N + 1)]
        uk = [[Nx[i].X, Nh[i].X, N_phi[i].X, t_total.X] for i in range(N + 1)]
        xk_all.append(xk)
        uk_all.append(uk)

        # Update kinematic equation parameters
        H_all, W_all, G_all, C_all = HWGc(xk, uk, delta_tao, N) 
        for i in range(1, N + 1):
            for j in range(8):
                constr = model.getConstrByName(f"motion_eq_{i}_{j}")
                for k in range(8):
                    model.chgCoeff(constr, x_det[i-1, k], float(H_all[i-1][j, k]))
                    model.chgCoeff(constr, x_det[i, k], float(W_all[i][j, k]))
                for k in range(4):
                    model.chgCoeff(constr, u_det[i-1, k], float(G_all[i-1][j, k]))
                    model.chgCoeff(constr, u_det[i, k], float(G_all[i][j, k]))
                rhs = -delta_tao / 2 * float(C_all[i-1][0, j] + C_all[i][0, j])
                constr.setAttr("RHS", rhs)

        # Update trust-region size
        sgm=1/(1+e**((iter+l1)/l2-l3))  
        delta=sgm*delta_0 
        for i in range(N + 1):
            model.getConstrByName(f"hp_trust_{i}").setAttr("RHS",xk[i][0] + delta[0])
            model.getConstrByName(f"hp_trust_{i}_neg").setAttr("RHS",xk[i][0] - delta[0])
            model.getConstrByName(f"xp_trust_{i}").setAttr("RHS",xk[i][1] + delta[1])
            model.getConstrByName(f"xp_trust_{i}_neg").setAttr("RHS",xk[i][1] - delta[1])
            model.getConstrByName(f"yp_trust_{i}").setAttr("RHS",xk[i][2] + delta[2])
            model.getConstrByName(f"yp_trust_{i}_neg").setAttr("RHS",xk[i][2] - delta[2])
            model.getConstrByName(f"v_trust_{i}").setAttr("RHS",xk[i][3] + delta[3])
            model.getConstrByName(f"v_trust_{i}_neg").setAttr("RHS",xk[i][3] - delta[3]) 
            model.getConstrByName(f"theta_trust_{i}").setAttr("RHS",xk[i][4] + delta[4])
            model.getConstrByName(f"theta_trust_{i}_neg").setAttr("RHS",xk[i][4] - delta[4])
            model.getConstrByName(f"psi_trust_{i}").setAttr("RHS",xk[i][5] + delta[5])
            model.getConstrByName(f"psi_trust_{i}_neg").setAttr("RHS",xk[i][5] - delta[5])
            model.getConstrByName(f"phi_trust_{i}").setAttr("RHS",xk[i][6] + delta[6])
            model.getConstrByName(f"phi_trust_{i}_neg").setAttr("RHS",xk[i][6] - delta[6])
            model.getConstrByName(f"tp_trust_{i}").setAttr("RHS",xk[i][7] + delta[7])
            model.getConstrByName(f"tp_trust_{i}_neg").setAttr("RHS",xk[i][7] - delta[7])

        # Update collision-avoidance constraints
        for i in range(N):
            p_i_k = [xk[i][1], xk[i][2], xk[i][0]]  # Aircraft position at current time
            for s in range(S):
                sd_obs1 = np.linalg.norm(p_i_k - O1_samples[s], 2)
                nabla = nabla_pS(p_i_k, O1_samples[s])
                constr = model.getConstrByName(f"escape_obs1_{i}_{s}")
                # Update coefficients of left-hand-side variables
                model.chgCoeff(constr, xp[i], float(nabla[0]))
                model.chgCoeff(constr, yp[i], float(nabla[1]))
                model.chgCoeff(constr, hp[i], float(nabla[2]))
                # Update right-hand side
                rhs = RO1 -  sd_obs1 + d_safe + (nabla[0]*p_i_k[0] + nabla[1]*p_i_k[1] + nabla[2]*p_i_k[2])
                constr.setAttr("RHS", rhs)

        O2_samples = get_obs_traj(O2, O2_else, S, N, v_obs_psi, t_total.X)
        for i in range(N):
            p_i_k = [xk[i][1], xk[i][2], xk[i][0]]  # Aircraft position at current time
            for s in range(S):
                sd_obs2 = np.linalg.norm(p_i_k - O2_samples[s][i], 2)
                nabla = nabla_pS(p_i_k, O2_samples[s][i])
                constr = model.getConstrByName(f"escape_obs2_{i}_{s}")
                # Update coefficients of left-hand-side variables
                model.chgCoeff(constr, xp[i], float(nabla[0]))
                model.chgCoeff(constr, yp[i], float(nabla[1]))
                model.chgCoeff(constr, hp[i], float(nabla[2]))
                # Update right-hand side
                rhs = RO2 -  sd_obs2 + d_safe + (nabla[0]*p_i_k[0] + nabla[1]*p_i_k[1] + nabla[2]*p_i_k[2])
                constr.setAttr("RHS", rhs)

    end_time = time.time()
    initial_time = end_time - begin_time

    # Write model to file
    # model.optimize()
    # model.write("aircraft_trajectory_optimization.lp")

    # Output all decision variable values to file
    # if model.Status == GRB.OPTIMAL:
    #     with open("solution.txt", "w") as f:
    #         f.write(f"Optimal Objective Value: {model.ObjVal}\n")
    #         for v in model.getVars():
    #             f.write(f"{v.VarName}: {v.X}\n")

    # Organize outputs
    xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all = organize_xk(N, xk_all)
    Nx_all, Nh_all, N_phi_all, t_total_all = organize_uk(N, uk_all)
    create_acmi(xk_all[-1], uk_all[-1], N, O1_samples, O2_samples)
    get_vio_percentage(xk_all[-1], N, O1, O2, O2_else, RO1, RO2, std1, std2, t_total_all[-1][-1])

    # Plot figures
    # plot_trajectory(N, iter, xp_all, yp_all, hp_all, O1_samples, RO1, O2_samples, RO2)
    # plot_results(N, iter, xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all, Nx_all, Nh_all, N_phi_all, t_total_all)

    return xk_all, uk_all, initial_time

if __name__ == "__main__":
    iter_initial = 10  # Set number of iterations
    xk_all, uk_all, initial_time = initial_traj(iter_initial)
    print(f"Initial Trajectory Optimization completed in {initial_time:.2f} seconds.")
