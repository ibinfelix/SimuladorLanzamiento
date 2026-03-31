import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root

# Air density at sea level, standard conditions (kg/m^3)
RHO = 1.225
# Gravity (m/s^2)
G = 9.81

def get_object_properties(obj_type, dimension, mass=None, density=None):
    Cd = 0.47
    A = 0.0
    V = 0.0
    
    if obj_type == "Sphere":
        r = dimension / 2.0
        A = np.pi * (r ** 2)
        V = (4/3) * np.pi * (r ** 3)
        Cd = 0.47
    elif obj_type == "Cube":
        A = dimension ** 2
        V = dimension ** 3
        Cd = 1.05
    elif obj_type == "Plate":
        A = dimension ** 2
        V = A * (0.1 * dimension)
        Cd = 1.28
    
    if mass is None and density is not None:
        mass = density * V
    elif mass is None and density is None:
        mass = 1.0

    return A, V, mass, Cd

def projectile_odes(t, state, m, A, Cd, wind_vector):
    x, y, z, vx, vy, vz = state
    v_vec = np.array([vx, vy, vz])
    wind_arr = np.array(wind_vector)
    
    v_rel = v_vec - wind_arr
    speed_rel = np.linalg.norm(v_rel)
    
    if speed_rel == 0:
        a_drag = np.zeros(3)
    else:
        a_drag = -0.5 * RHO * Cd * A * speed_rel * v_rel / m
        
    a_grav = np.array([0, 0, -G])
    a_total = a_drag + a_grav
    return [vx, vy, vz, a_total[0], a_total[1], a_total[2]]

def simulate_trajectory(v0_x, v0_y, v0_z, m, A, Cd, wind_vector, max_time=60.0):
    state0 = [0, 0, 0, v0_x, v0_y, v0_z]
    
    def hit_ground(t, state, *args):
        return state[2]
    hit_ground.terminal = True
    hit_ground.direction = -1
    
    res = solve_ivp(
        fun=projectile_odes,
        t_span=(0, max_time),
        y0=state0,
        events=[hit_ground],
        args=(m, A, Cd, wind_vector),
        max_step=0.05,
    )
    return res.t, res.y

def find_launch_velocity(target_dist, target_height, m, A, Cd, wind_vector):
    # Initial guess without drag
    v0z_guess = np.sqrt(2 * G * target_height) if target_height > 0 else 5.0
    try:
        time_to_peak = v0z_guess / G
        total_time = 2 * time_to_peak
        v0x_guess = target_dist / total_time
    except ZeroDivisionError:
        v0x_guess = 10.0
    v0y_guess = 0.0
    
    guess = [v0x_guess, v0y_guess, v0z_guess]
    
    def root_func(v_guess):
        vX, vY, vZ = v_guess
        if vZ <= 0:
            return [1e5, 1e5, 1e5]
            
        t, y = simulate_trajectory(vX, vY, vZ, m, A, Cd, wind_vector, max_time=60.0)
        
        if len(t) < 2:
            return [1e5, 1e5, 1e5]
            
        final_x = y[0][-1]
        final_y = y[1][-1]
        max_z = np.max(y[2])
        
        err_dist = final_x - target_dist
        err_y = final_y - 0.0
        err_height = max_z - target_height
        
        return [err_dist, err_y, err_height]
        
    res = root(root_func, guess, method='hybr', tol=0.1)
    
    return res.x

def calculate_launcher_forces(v0_mag, mass, launcher_type, **kwargs):
    kinetic_energy = 0.5 * mass * (v0_mag**2)
    
    if launcher_type == "Linear Piston":
        stroke_length = kwargs.get('stroke_length', 1.0)
        force = kinetic_energy / stroke_length if stroke_length > 0 else 0
        return {"Force Required (N)": force}
        
    elif launcher_type == "Wheel Rollers":
        wheel_radius = kwargs.get('wheel_radius', 0.1)
        contact_length = kwargs.get('contact_length', 0.2)
        force = kinetic_energy / contact_length if contact_length > 0 else 0
        torque = (force / 2) * wheel_radius
        rpm = (v0_mag / wheel_radius) * (60 / (2*np.pi)) if wheel_radius > 0 else 0
        return {
            "Total Forward Force (N)": force,
            "Torque per Wheel (N.m)": torque,
            "Wheel Speed (RPM)": rpm
        }
        
    elif launcher_type == "Blast Force":
        blast_duration = kwargs.get('blast_duration', 0.05)
        force = (mass * v0_mag) / blast_duration if blast_duration > 0 else 0
        return {"Average Peak Force (N)": force}
        
    return {}
