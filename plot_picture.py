import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

def plot_trajectory(N, iter, xp_all, yp_all, hp_all, O1_samples, RO1, O2_samples, RO2):
    label_fontsize_3d = 20
    ticks_fontsize_3d = 16
    legend_fontsize_3d = 18


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x (m)',labelpad = 10,fontsize=label_fontsize_3d)
    ax.set_ylabel('y (m)',labelpad = 10,fontsize=label_fontsize_3d)
    ax.set_zlabel('h (m)',labelpad = 10,fontsize=label_fontsize_3d)
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(xp_all[k], yp_all[k], hp_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k>0 and k<iter:
            ax.plot(xp_all[k], yp_all[k], hp_all[k],color='black',linewidth=0.5+k*0.08)
        else:
            ax.plot(xp_all[k], yp_all[k], hp_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)

    u = np.linspace(0, 2 * np.pi, 100)
    v_half = np.linspace(0, np.pi/2, 50)  
    v_whole = np.linspace(0, np.pi, 100)

    
    for sample in O1_samples:
        ax.plot(sample[0], sample[1], sample[2], color = 'gray')
        x = sample[0] + RO1 * np.outer(np.cos(u), np.sin(v_half))
        y = sample[1] + RO1 * np.outer(np.sin(u), np.sin(v_half))
        z = sample[2] + RO1 * np.outer(np.ones(np.size(u)), np.cos(v_half))
        ax.plot_surface(x, y, z, color='gray', alpha=0.2)

    
    for sample in O2_samples:
        ax.plot(sample[:, 0], sample[:, 1], sample[:, 2], color='gray', alpha=0.3)

    
    for i in [-1,-5]:
        sample = O2_samples[0]
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = sample[i, 0] + RO2 * np.outer(np.cos(u), np.sin(v))
        y = sample[i, 1] + RO2 * np.outer(np.sin(u), np.sin(v))
        z = sample[i, 2] + RO2 * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color='gray', alpha=0.3)


    
    ax.set_xlim([0, 16000])
    ax.set_ylim([-8000, 8000])
    ax.set_zlim([0, 8000])
    ax.set_xticks(np.linspace(0,16000,9))
    ax.set_yticks(np.linspace(-8000,8000,9))
    ax.set_zticks(np.linspace(0,8000,9))
    plt.xticks(fontsize=ticks_fontsize_3d) 
    plt.yticks(fontsize=ticks_fontsize_3d) 
    ax.tick_params(axis='z', labelsize=ticks_fontsize_3d, pad=5) 
    ax.set_box_aspect([1, 1, 0.5]) 
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='lower right', bbox_to_anchor=(0.9, 0.6))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize_3d)  

    plt.show()


def plot_results(N, iter, xp_all, yp_all, hp_all, v_all, theta_all, psi_all, phi_all, tp_all, Nx_all, Nh_all, N_phi_all, t_total_all):
    label_fontsize = 26
    ticks_fontsize = 24
    legend_fontsize = 22
    tau = [i/N for i in range(N+1)]


    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel('Iteration', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$t_{total}$ (s)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    ax.plot(range(iter+1), [t_total_all[k][-1] for k in range(iter+1)], color='blue', linewidth=3, marker='o', markersize=8)
    plt.show()

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$',labelpad = 10, fontsize=label_fontsize)
    ax.set_ylabel(r'$x$ (m)',labelpad = 10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, xp_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, xp_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, xp_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$',labelpad = 10, fontsize=label_fontsize)
    ax.set_ylabel(r'$y$ (m)',labelpad = 10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, yp_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, yp_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, yp_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()
    
    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$',labelpad = 10, fontsize=label_fontsize)
    ax.set_ylabel(r'$h$ (m)',labelpad = 10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, hp_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, hp_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, hp_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$',labelpad = 10, fontsize=label_fontsize)
    ax.set_ylabel(r'$v$ (m/s)',labelpad = 10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, v_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, v_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, v_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()


    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$\theta$ (rad)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, theta_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, theta_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, theta_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()


    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$\psi$ (rad)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, psi_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, psi_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, psi_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()
    

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$\phi$ (rad)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, phi_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, phi_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, phi_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()
    

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$N_x$ (rad)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, Nx_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, Nx_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, Nx_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()
    

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$N_z$ (rad)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, Nh_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, Nh_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, Nh_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()
    

    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel(r'$\tau$', labelpad=10, fontsize=label_fontsize)
    ax.set_ylabel(r'$N_{\phi}$ (rad)', labelpad=10, fontsize=label_fontsize)
    plt.xticks(fontsize=ticks_fontsize) 
    plt.yticks(fontsize=ticks_fontsize) 
    for k in range(iter+1):  #k=0,...,iter
        if k == 0:
            ax.plot(tau, N_phi_all[k], label='iteration history',color='orange',linewidth=2.5, linestyle='--')
        elif k > 0 and k < iter:
            ax.plot(tau, N_phi_all[k], color='black',linewidth=0.5+k*0.1)
        else:
            ax.plot(tau, N_phi_all[k], label='converged trajectory',color='blue',linewidth=3, marker='o',markersize=10)
    
    custom_lines = [Line2D([0], [0], color='orange',linewidth=2, linestyle='--'),
                    Line2D([0], [0], color='black',linewidth=1),
                    Line2D([0], [0], color='blue',linewidth=3, marker='o',markersize=10)]
    legend = ax.legend(custom_lines, ['First Step', 'Intermediate Steps', 'Last Step'],loc='upper right', bbox_to_anchor=(1, 1))
    
    frame = legend.get_frame()
    frame.set_linewidth(1.5)  
    
    for text in legend.get_texts():
        text.set_fontsize(legend_fontsize)  
    plt.show()
