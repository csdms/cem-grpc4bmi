#!/usr/bin/env python
# Run the [Coastline Evolution Model](https://csdms.colorado.edu/wiki/Model:CEM)
# (CEM) in Python through [grpc4bmi](https://grpc4bmi.readthedocs.io).
# 
# CEM addresses predominately sandy, wave-dominated coastlines on time-scales
# ranging from years to millenia and on spatial scales ranging from kilometers
# to hundreds of kilometers. Shoreline evolution results from gradients in
# wave-driven alongshore sediment transport. At its most basic level, the model
# follows the standard 'one-line' modeling approach, where the cross-shore
# dimension is collapsed into a single data point. However, the model allows the
# plan-view shoreline to take on arbitrary local orientations, and even fold
# back upon itself, as complex shapes such as capes and spits form under some
# wave climates (distributions of wave influences from different approach
# angles). The model can also represent the geology underlying the sandy
# coastline and shoreface in a simplified manner and enables the simulation of
# coastline evolution when sediment supply from an eroding shoreface may be
# constrained. CEM also supports the simulation of human manipulations to
# coastline evolution through beach nourishment or hard structures.
# 
# View the model source code and its BMI at
# https://github.com/csdms-contrib/cem/tree/v0.

# Start by importing some helper libraries.
import os
import pathlib
import numpy as np
import math
import matplotlib.pyplot as plt
from tqdm import trange

# Next, import the grpc4bmi Docker client.
from grpc4bmi.bmi_client_docker import BmiClientDocker

# Set variables:
# * which Docker image to use,
# * the port exposed through the image, and
# * the location of the configuration file used for the model.
DOCKER_IMAGE = "csdms/cem-grpc4bmi:latest"
BMI_PORT = 55555
CONFIG_FILE = pathlib.Path("cem.txt")

# Create a model instance, `m`, through the grpc4bmi Docker client.
m = BmiClientDocker(image=DOCKER_IMAGE, image_port=BMI_PORT, work_dir=".")

# Show the name of the model.
m.get_component_name()

# Start CEM through its BMI with a configuration file.
m.initialize(str(CONFIG_FILE))

# Show the input and output variables for the model.
m.get_input_var_names(), m.get_output_var_names()

# Check time information provided by the model.
print("Start time:", m.get_start_time())
print("End time:", m.get_end_time())
print("Current time:", m.get_current_time())
print("Time step:", m.get_time_step())
print("Time units:", m.get_time_units())

# The main output variable for this model is sea water depth
# (using the CSDMS Standard Name `sea_water__depth`).
# Get the identifier for the grid on which this variable is defined.
grid_id = m.get_var_grid('sea_water__depth')
print("Grid id:", grid_id)

# Get attributes of the grid.
print("Grid type:", m.get_grid_type(grid_id))
rank = m.get_grid_rank(grid_id)
print("Grid rank:", rank)
shape = np.ndarray(rank, dtype=int)
m.get_grid_shape(grid_id, shape)
print("Grid shape:", shape)
spacing = np.ndarray(rank, dtype=float)
m.get_grid_spacing(grid_id, spacing)
print("Grid spacing:", spacing)

# Allocate memory for the sea water depth variable and get its current values from CEM.
# Note that *get_value* expects a one-dimensional array to receive output.
z = np.empty(shape, dtype=float).flatten()
m.get_value('sea_water__depth', z)
z.reshape(shape)

# Define a convenience function for plotting.
def plot_coast(depth, spacing=(1000,1000)):
    xmin, xmax = 0., depth.shape[1] * spacing[0] * 1e-3
    ymin, ymax = 0., depth.shape[0] * spacing[1] * 1e-3

    plt.imshow(depth, extent=[xmin, xmax, ymin, ymax], origin='lower', cmap='ocean', aspect="auto")
    plt.colorbar().ax.set_ylabel('Water Depth (m)')
    plt.xlabel('Along shore (km)')
    plt.ylabel('Cross shore (km)')

# This function generates plots that look like the one below. We begin with a flat delta (green) and a linear coastline at `y` = 30 km. The bathymetry drops off linearly to the top of the domain.
plot_coast(z.reshape(shape))
plt.savefig("shoreline_initial.png", dpi=96)
plt.close()

# Before running the model, set a few input parameters.
# These parameters represent the wave height, wave period, and wave angle of the incoming waves to the coastline.
_one = np.ones(1, dtype=float)
m.set_value("sea_surface_water_wave__height", _one * 2.0)
m.set_value("sea_surface_water_wave__period", _one * 7.0)
m.set_value("sea_surface_water_wave__azimuth_angle_of_opposite_of_phase_velocity", _one * math.radians(45))

# Add sediment discharge to the ocean at a set of 10 cells on the shoreline.
# Allocate memory for the sediment discharge array and set the discharge at the coastal cells to some value.
qs = np.zeros_like(z.reshape(shape))
qs[0, 295:305] = 5000
qs

# Run the model, updating the bedload flux at each time step.
n_days = 360
n_time_steps = int(n_days / m.get_time_step())
for _ in trange(n_time_steps):
    m.set_value("land_surface_water_sediment~bedload__mass_flow_rate", qs)
    m.update()

# Get the final values of sea water depth and display them.
m.get_value("sea_water__depth", z)
plot_coast(z.reshape(shape))
plt.savefig("shoreline_final.png", dpi=96)
plt.close()

# Stop the model and clean up any resources it allocates.
m.finalize()

# Stop the container running through grpc4bmi.
# This is needed by grpc4bmi to properly deallocate the resources it uses.
# It may take a few moments.
del m
