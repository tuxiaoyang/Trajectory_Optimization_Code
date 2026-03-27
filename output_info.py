import csv
import os
import numpy as np
from tools import EN2LonLat


def organize_xk(N, xk_all):
    xp_all = []
    yp_all = []
    hp_all = []
    v_all = []
    theta_all = []
    psi_all = []
    phi_all = []
    tp_all = []
    for xk in xk_all:
        xp_all.append([xk[i][1] for i in range(N + 1)])
        yp_all.append([xk[i][2] for i in range(N + 1)])
        hp_all.append([xk[i][0] for i in range(N + 1)])
        v_all.append([xk[i][3] for i in range(N + 1)])
        theta_all.append([xk[i][4] for i in range(N + 1)])
        psi_all.append([xk[i][5] for i in range(N + 1)])
        phi_all.append([xk[i][6] for i in range(N + 1)])
        tp_all.append([xk[i][7] for i in range(N + 1)])

    return xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all

def organize_uk(N, uk_all):
    Nx_all = []
    Nh_all = []
    N_phi_all = []
    t_total_all = []
    for uk in uk_all:
        Nx_all.append([uk[i][0] for i in range(N+1)])
        Nh_all.append([uk[i][1] for i in range(N+1)])
        N_phi_all.append([uk[i][2] for i in range(N+1)])
        t_total_all.append([uk[i][3] for i in range(N+1)])

    return Nx_all, Nh_all, N_phi_all, t_total_all


def create_csv(N, iter, xk_all, uk_all):

    # Create 'result' directory if it doesn't exist
    result_dir = 'result'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all = organize_xk(N, xk_all)
    Nx_all, Nh_all, N_phi_all, t_total_all = organize_uk(N, uk_all)

    for k in range(iter + 1):
        with open(f'{result_dir}/output_x_{k}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            headers = ['xp', 'yp', 'hp', 'v', 'theta', 'psi', 'phi', 'tp']
            writer.writerow(headers)

            # Write data
            for j in range(N + 1):
                writer.writerow([xp_all[k][j], yp_all[k][j], hp_all[k][j], v_all[k][j],
                                 theta_all[k][j], psi_all[k][j], phi_all[k][j], tp_all[k][j]])

        with open(f'{result_dir}/output_u_{k}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            headers = ['Nx', 'Nh', 'N_phi', 't_total']
            writer.writerow(headers)

            # Write data
            for j in range(N + 1):
                writer.writerow([Nx_all[k][j], Nh_all[k][j], N_phi_all[k][j], t_total_all[k][j]])

def create_acmi(xk, uk, N, O1_samples, O2_samples):

    hp = [xk[i][0] for i in range(N + 1)]
    xp = [xk[i][1] for i in range(N + 1)]
    yp = [xk[i][2] for i in range(N + 1)]
    theta = [xk[i][4] for i in range(N + 1)]
    psi = [xk[i][5] for i in range(N + 1)]
    phi = [xk[i][6] for i in range(N + 1)]


    planename = '1'
    planetype = 'J-10'
    planetypeinfo = 'Type=Air+FixedWing,Pilot=David_{},Coalition=Allies,Color=Red,Country=ru,Name={}'.format(planename, planetype)
    acmi_result=['FileType=text/acmi/tacview\n','FileVersion=2.1\n']

    # Generate longitude and latitude information for the result trajectory:
    lonp=[]
    latp=[]
    for i in range(N+1):  #i=0,...,N
        lon_i, lat_i = EN2LonLat(yp[i],xp[i],0,0)
        lonp.append(lon_i)
        latp.append(lat_i)

    # Read obstacle trajectory information
    interceptor1name = '2'
    interceptor1type = 'J-10'
    interceptor1typeinfo = 'Type=Air+FixedWing,Pilot=David_{},Coalition=Allies,Color=Blue,Country=ru,Name={}'.format(interceptor1name, interceptor1type)
    lon0 = 0
    lat0 = 0
    inter1_lon = []
    inter1_lat = []
    for i in range(N):
        lon_i, lat_i = EN2LonLat(O2_samples[0][i][1],O2_samples[0][i][0],0,0)
        inter1_lon.append(lon_i)
        inter1_lat.append(lat_i)

    for i in range(N+1): #i=0,...,N
        timeinfo = '#{:.2f}'.format(uk[-1][-1]/N*i)
        planestateinfo = '{:.7f}|{:.7f}|{:.2f}|{:.1f}|{:.1f}|{:.1f}'.format(lonp[i], latp[i], hp[i], -phi[i]*57.3, theta[i]*57.3, -psi[i]*57.3)
        if i < N:
            interception1info = '{:.7f}|{:.7f}|{:.2f}'.format(inter1_lon[i], inter1_lat[i], O2_samples[0][i][2])
        fullInfo = '{}\n{},T={},{}\n'.format(timeinfo, planename, planestateinfo, planetypeinfo)
        if i == 0:
            fullInfo = '{}\n{},T={},{}\n{},T={},{}\n'.format(timeinfo, planename, planestateinfo, planetypeinfo, interceptor1name, interception1info, interceptor1typeinfo)
        else:
            fullInfo = '{}\n{},T={}\n{},T={}\n'.format(timeinfo, planename, planestateinfo, interceptor1name, interception1info)
        acmi_result.append(fullInfo)
    write_acmi(acmi_result) # Save as acmi file

def write_acmi(acl):
    result_dir = 'result'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    acmi_path = os.path.join(result_dir, 'acmi.acmi')
    with open(acmi_path, 'w') as a:
        a.truncate(0)   # Clear content
        a.writelines(acl)


def get_vio_percentage(xk, N, O1, O2, O2_else, RO1, RO2, std1, std2, t_total):
    from tools import get_obs_traj

    vio_count_all = []
    vio_count1 = []
    vio_count2 = []
    t_num = 10000

    hp = [xk[i][0] for i in range(N + 1)]
    xp = [xk[i][1] for i in range(N + 1)]
    yp = [xk[i][2] for i in range(N + 1)]

    O1_samples = O1 + np.hstack((np.random.normal(0, std1, (t_num, 2)), np.zeros((t_num, 1))))
    v_obs_psi = np.random.normal(0, std2, t_num)
    O2_samples = get_obs_traj(O2, O2_else, t_num, N, v_obs_psi, t_total)

    for i in range(N):
        vio_count_all.append(0)
        vio_count1.append(0)
        vio_count2.append(0)
        for j in range(t_num):
            # Calculate distance to obstacle 1
            dist_O1 = ((xp[i] - O1_samples[j][0]) ** 2 + (yp[i] - O1_samples[j][1]) ** 2 + (hp[i] - O1_samples[j][2]) ** 2) ** 0.5
            if dist_O1 < RO1:
                vio_count1[-1] += 1
                vio_count_all[-1] += 1

            # Calculate distance to obstacle 2
            dist_O2 = ((xp[i] - O2_samples[j][i][0]) ** 2 + (yp[i] - O2_samples[j][i][1]) ** 2 + (hp[i] - O2_samples[j][i][2]) ** 2) ** 0.5
            if dist_O2 < RO2:
                vio_count2[-1] += 1
                vio_count_all[-1] += 1

        vio_count1[-1] /= t_num
        vio_count2[-1] /= t_num
        vio_count_all[-1] /= t_num

    print("Total Violations:", vio_count_all)
    print("Violations for Obstacle 1:", vio_count1)
    print("Violations for Obstacle 2:", vio_count2)