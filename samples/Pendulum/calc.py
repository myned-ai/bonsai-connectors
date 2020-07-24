import numpy as np

def step(u, th, thdot):


    g = 10.0
    m = 1.0
    l = 1.0
    dt = 0.05

    u = np.clip(u, -2, 2)[0]

    newthdot = thdot + (-3*g/(2*l) * np.sin(th + np.pi) + 3./(m*l**2)*u) * dt
    newth = th + newthdot*dt
    newthdot = np.clip(newthdot, -8, 8) #pylint: disable=E1111

    print("theta: {} cos_theta: {}  theta_deg: {}   theta_dot: {}".format(newth, np.cos(newth), np.rad2deg(newth), newthdot))
    return newth, newthdot




newth = np.arccos(-0.707)
newthdot = 0.0
for x in range(0,10):  
    newth, newthdot = step([-2.0], newth, newthdot)

#for x in range(0,10):        
#    newth, newthdot = step([-2.0], newth, newthdot)

