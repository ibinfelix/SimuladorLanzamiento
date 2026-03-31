import streamlit as st
import numpy as np
import plotly.graph_objects as go
import physics

st.set_page_config(page_title="Object Launcher Simulator", layout="wide")

st.title("Object Launcher Simulator")

# Sidebar
st.sidebar.header("Target Variables")
target_dist = st.sidebar.number_input("Target Distance (m)", min_value=1.0, value=50.0, step=1.0)
target_height = st.sidebar.number_input("Target Max Height (m)", min_value=1.0, value=15.0, step=1.0)

st.sidebar.header("Object Settings")
obj_type = st.sidebar.selectbox("Object Type", ["Sphere", "Cube", "Plate"])
dimension = st.sidebar.number_input("Base Dimension (m)", min_value=0.01, value=0.2, step=0.01)

mass_or_density = st.sidebar.radio("Use Mass or Density?", ["Mass (kg)", "Density (kg/m^3)"])
if mass_or_density == "Mass (kg)":
    mass = st.sidebar.number_input("Mass (kg)", min_value=0.01, value=1.0, step=0.1)
    density = None
else:
    density = st.sidebar.number_input("Density (kg/m^3)", min_value=1.0, value=1000.0, step=10.0)
    mass = None

st.sidebar.header("Environment Settings")
wind_x = st.sidebar.number_input("Wind X (m/s) [Headwind/Tailwind]", value=0.0, step=1.0)
wind_y = st.sidebar.number_input("Wind Y (m/s) [Crosswind]", value=0.0, step=1.0)
wind_z = 0.0

st.sidebar.header("Launcher Settings")
launcher_type = st.sidebar.selectbox("Launcher Type", ["Wheel Rollers", "Linear Piston", "Blast Force"])

launcher_kwargs = {}
if launcher_type == "Wheel Rollers":
    launcher_kwargs['wheel_radius'] = st.sidebar.number_input("Wheel Radius (m)", min_value=0.01, value=0.1)
    launcher_kwargs['contact_length'] = st.sidebar.number_input("Contact Length (m)", min_value=0.01, value=dimension)
elif launcher_type == "Linear Piston":
    launcher_kwargs['stroke_length'] = st.sidebar.number_input("Stroke Length (m)", min_value=0.1, value=1.0)
elif launcher_type == "Blast Force":
    launcher_kwargs['blast_duration'] = st.sidebar.number_input("Blast Duration (s)", min_value=0.01, value=0.05)


st.write("---")

if st.button("Simulate"):
    with st.spinner("Calculating Trajectory..."):
        A, V, final_mass, Cd = physics.get_object_properties(obj_type, dimension, mass, density)
        wind_vector = [wind_x, wind_y, wind_z]
        
        # 1. Find the required initial velocities
        v0x, v0y, v0z = physics.find_launch_velocity(target_dist, target_height, final_mass, A, Cd, wind_vector)
        
        v0_mag = np.linalg.norm([v0x, v0y, v0z])
        
        # 2. Simulate the trajectory for plotting
        t, y = physics.simulate_trajectory(v0x, v0y, v0z, final_mass, A, Cd, wind_vector)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Required Launch Speed", f"{v0_mag:.2f} m/s")
        if len(t) > 0:
            c2.metric("Flight Time", f"{t[-1]:.2f} s")
        else:
             c2.metric("Flight Time", "N/A")
             
        horizontal_speed = np.sqrt(v0x**2 + v0y**2)
        if horizontal_speed > 0:
            c3.metric("Required Elevation Angle", f"{np.degrees(np.arctan2(v0z, horizontal_speed)):.2f}°")
        else:
            c3.metric("Required Elevation Angle", "90.00°")
            
        c4, c5, c6 = st.columns(3)
        c4.metric("Azimuth Correction Angle (for crosswind)", f"{np.degrees(np.arctan2(v0y, v0x)):.2f}°")
        c5.metric("Object Mass", f"{final_mass:.2f} kg")
        c6.metric("Object Drag Area", f"{A:.4f} m^2")
        
        st.subheader("Launcher Mechanical Requirements")
        forces = physics.calculate_launcher_forces(v0_mag, final_mass, launcher_type, **launcher_kwargs)
        
        fc = st.columns(len(forces))
        for col, (k, val) in zip(fc, forces.items()):
            col.metric(k, f"{val:.2f}")
            
        st.write("---")
        st.subheader("Trajectory Visualization")
        
        # Plot 3D Trajectory
        x_vals = y[0]
        y_vals = y[1]
        z_vals = y[2]
        
        max_dim = max(np.max(x_vals), np.max(np.abs(y_vals)), np.max(z_vals), target_dist)
        
        fig = go.Figure()
        
        # The trajectory
        fig.add_trace(go.Scatter3d(
            x=x_vals, y=y_vals, z=z_vals,
            mode='lines',
            line=dict(color='blue', width=4),
            name="Trajectory"
        ))
        
        # The target marker
        fig.add_trace(go.Scatter3d(
            x=[target_dist], y=[0], z=[0],
            mode='markers',
            marker=dict(color='red', size=8, symbol='x'),
            name="Target Landing Spot"
        )) # Ground projection
        fig.add_trace(go.Scatter3d(
             x=x_vals, y=y_vals, z=np.zeros_like(z_vals),
             mode='lines',
             line=dict(color='black', width=2, dash='dash'),
             name="Ground Footprint"
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Forward Distance X (m)',
                yaxis_title='Cross Deviation Y (m)',
                zaxis_title='Height Z (m)',
                aspectmode='cube',
                xaxis=dict(range=[0, max_dim]),
                yaxis=dict(range=[-max_dim/2, max_dim/2]),
                zaxis=dict(range=[0, max_dim]),
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Click 'Simulate' to calculate physics and plot the trajectory.")
