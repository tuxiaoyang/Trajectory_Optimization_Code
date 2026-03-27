import numpy as np
from sympy import sin,cos

def txf(xk,uk,delta_tao,N):
    A=[]
    B=[]
    H=[]    
    G=[]
    C=[]
    W=[]
    for i in range(N+1):  # translated comment
        hi = xk[i][0]
        xpi = xk[i][1]
        ypi = xk[i][2]
        vi = xk[i][3]
        thetai = xk[i][4]
        psii = xk[i][5]
        phii = xk[i][6]
        ti = xk[i][7]
        Nxi = uk[i][0]
        Nhi = uk[i][1]
        phidoti = uk[i][2]
        uti = uk[i][3]
        Ai=jacobi_A(hi,xpi,ypi,vi,thetai,psii,phii,ti,Nxi,Nhi,phidoti,uti)
        Hi=np.identity(8)+0.5*delta_tao*Ai
        Wi=-np.identity(8)+0.5*delta_tao*Ai
        Bi=jacobi_B(hi,xpi,ypi,vi,thetai,psii,phii,ti,Nxi,Nhi,phidoti,uti)
        Gi=0.5*delta_tao*Bi
        ci=fxtao(xk[i],uk[i])-np.dot(Ai,xk[i])-np.dot(Bi,uk[i])
        C.append(ci)
        A.append(Ai)
        H.append(Hi)
        W.append(Wi)
        B.append(Bi)
        G.append(Gi)
    a=np.identity(8)    # translated comment
    b=np.zeros((8,8*N))
    Ma=np.column_stack((a,b))
    for i in range(N):  # translated comment
        a=np.zeros((8,8*i))
        b=H[i]
        c=W[i+1]
        d=np.zeros((8,8*(N-1-i)))
        Ma_next=np.column_stack((a,b,c,d))  # translated comment
        Ma=np.row_stack((Ma,Ma_next))  # translated comment
    
    Mb=np.zeros((8,4*(N+1)))
    for i in range(N):  # translated comment
        a=np.zeros((8,4*i))
        b=G[i]
        c=G[i+1]
        d=np.zeros((8,4*(N-1-i)))
        Mb_next=np.column_stack((a,b,c,d))
        Mb=np.row_stack((Mb,Mb_next))
    
    M=np.column_stack((Ma,Mb))    # translated comment
    F=(-2/delta_tao)*np.array(xk[0])
    for i in range(N):    # translated comment
        
        ciPluscip=np.array([C[i][0,0]+C[i+1][0,0],C[i][0,1]+C[i+1][0,1],C[i][0,2]+C[i+1][0,2],C[i][0,3]+C[i+1][0,3],C[i][0,4]+C[i+1][0,4],C[i][0,5]+C[i+1][0,5],C[i][0,6]+C[i+1][0,6],C[i][0,7]+C[i+1][0,7]])    
        F=np.hstack((F,ciPluscip))  # translated comment
    F=(-0.5*delta_tao)*F     # translated comment

    return M,F

def HWGc(xk,uk,delta_tao,N):
    H=[]
    W=[]    
    G=[]
    C=[]
    for i in range(N+1):  # translated comment
        hi = xk[i][0]
        xpi = xk[i][1]
        ypi = xk[i][2]
        vi = xk[i][3]
        thetai = xk[i][4]
        psii = xk[i][5]
        phii = xk[i][6]
        ti = xk[i][7]
        Nxi = uk[i][0]
        Nhi = uk[i][1]
        phidoti = uk[i][2]
        uti = uk[i][3]
        Ai=jacobi_A(hi,xpi,ypi,vi,thetai,psii,phii,ti,Nxi,Nhi,phidoti,uti)
        Hi=np.identity(8)+0.5*delta_tao*Ai
        Wi=-np.identity(8)+0.5*delta_tao*Ai
        Bi=jacobi_B(hi,xpi,ypi,vi,thetai,psii,phii,ti,Nxi,Nhi,phidoti,uti)
        Gi=0.5*delta_tao*Bi
        ci=fxtao(xk[i],uk[i])-np.dot(Ai,xk[i])-np.dot(Bi,uk[i])
        C.append(ci)
        H.append(Hi)
        W.append(Wi)
        G.append(Gi)
        
    return H, W, G, C

def fxtao(x,u):    # translated comment
    g = 9.81
    h=x[0]
    xp=x[1]
    yp=x[2]
    v=x[3]
    theta=x[4]
    psi=x[5]
    phi=x[6]
    t=x[7]
    Nx=u[0]
    Nh=u[1]
    phidot=u[2]
    ut=u[3]
    f1=ut*v*sin(theta)
    f2=ut*v*cos(theta)*cos(psi)
    f3=ut*v*cos(theta)*sin(psi)
    f4=ut*(Nx-sin(theta))*g
    f5=(Nh*cos(phi)-cos(theta))*g*ut/v
    f6=Nh*sin(phi)*g*ut/(v*cos(theta))
    f7=ut*phidot
    f8=ut
    return np.array([f1,f2,f3,f4,f5,f6,f7,f8])


# translated comment
def jacobi_A(h,xp,yp,v,theta,psi,phi,t,Nx,Nh,phidot,ut):
    g=9.81
    A1=np.array([0, 0, 0, ut*sin(theta), ut*v*cos(theta), 0, 0, 0])  # translated comment
    A2=np.array([0, 0, 0, ut*cos(psi)*cos(theta), -ut*v*sin(theta)*cos(psi), -ut*v*sin(psi)*cos(theta), 0, 0])  # translated comment
    A3=np.array([0, 0, 0, ut*sin(psi)*cos(theta), -ut*v*sin(psi)*sin(theta), ut*v*cos(psi)*cos(theta), 0, 0])  # translated comment
    A4=np.array([0, 0, 0, 0, -g*ut*cos(theta), 0, 0, 0])  # translated comment
    A5=np.array([0, 0, 0, -g*ut*(Nh*cos(phi) - cos(theta))/v**2, g*ut*sin(theta)/v, 0, -Nh*g*ut*sin(phi)/v, 0])  # translated comment
    A6=np.array([0, 0, 0, -Nh*g*ut*sin(phi)/(v**2*cos(theta)), Nh*g*ut*sin(phi)*sin(theta)/(v*cos(theta)**2), 0, Nh*g*ut*cos(phi)/(v*cos(theta)), 0])  # translated comment
    A7=np.array([0, 0, 0, 0, 0, 0, 0, 0])  # translated comment
    A8=np.array([0, 0, 0, 0, 0, 0, 0, 0])  # translated comment
    
    A=np.matrix([A1,A2,A3,A4,A5,A6,A7,A8])
    return A

# translated comment
def jacobi_B(h,xp,yp,v,theta,psi,phi,t,Nx,Nh,phidot,ut):
    g=9.81
    B1=np.array([0, 0, 0, v*sin(theta)])  # translated comment
    B2=np.array([0, 0, 0, v*cos(psi)*cos(theta)])  # translated comment
    B3=np.array([0, 0, 0, v*sin(psi)*cos(theta)])  # translated comment
    B4=np.array([g*ut, 0, 0, g*(Nx - sin(theta))])  # translated comment
    B5=np.array([0, g*ut*cos(phi)/v, 0, g*(Nh*cos(phi) - cos(theta))/v])  # translated comment
    B6=np.array([0, g*ut*sin(phi)/(v*cos(theta)), 0, Nh*g*sin(phi)/(v*cos(theta))])  # translated comment
    B7=np.array([0, 0, ut, phidot])  # translated comment
    B8=np.array([0, 0, 0, 1])  # translated comment
    
    B=np.matrix([B1,B2,B3,B4,B5,B6,B7,B8])
    return B

def nabla_pS(pu, O): # translated comment
    Ox = O[0]
    Oy = O[1]
    Oh = O[2]
    xp = pu[0]
    yp = pu[1]
    h = pu[2]
    n_pS = np.zeros(3)
    n_pS[0] = (-Ox + xp)/(np.sqrt((-Oh + h)**2 + (-Ox + xp)**2 + (-Oy + yp)**2)+1e-6)
    n_pS[1] = (-Oy + yp)/(np.sqrt((-Oh + h)**2 + (-Ox + xp)**2 + (-Oy + yp)**2)+1e-6)
    n_pS[2] = (-Oh + h)/(np.sqrt((-Oh + h)**2 + (-Ox + xp)**2 + (-Oy + yp)**2)+1e-6)
    return n_pS


def get_obs_traj(O2, O2_else, num_S, N, v_obs_psi, t_total): # translated comment
    tau = t_total/N
    v = O2_else[0]
    theta = O2_else[1]
    psi = O2_else[2]
    v_theta = 0
    v_psi = v_obs_psi

    O2_samples = []
    for s in range(num_S):
        O2_samples_s = np.zeros((N+1, 3))
        O2_samples_s[0] = O2
        psi_s = psi
        theta_s = theta
        for i in range(N):
            vx = v * np.cos(theta) * np.cos(psi_s)
            vy = v * np.cos(theta) * np.sin(psi_s)
            vz = v * np.sin(theta)
            
            O2_samples_s[i+1, 0] = O2_samples_s[i, 0] + tau * vx
            O2_samples_s[i+1, 1] = O2_samples_s[i, 1] + tau * vy
            O2_samples_s[i+1, 2] = O2_samples_s[i, 2] + tau * vz
            
            psi_s += tau * v_psi[s]
            theta_s += tau * v_theta
        
        O2_samples.append(O2_samples_s)  

    return O2_samples


def EN2LonLat(x, y, a, b):
    """
    (a, b)-(x, y)(lon, lat)
    :
        y: （）， -y
        x: （）
        a: （）
        b: （）
    :
        lon: （）
        lat: （）
    """
    # translated comment
    R = 6378137.0
    # translated comment
    dlat = y / R * (180 / np.pi)
    # translated comment
    dlon = -x / (R * np.cos(np.deg2rad(b))) * (180 / np.pi)
    lat = b + dlat
    lon = a + dlon
    return lon, lat
