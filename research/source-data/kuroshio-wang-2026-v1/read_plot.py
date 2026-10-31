import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import os

# ================= Set paths and parameters =================
example_file = r'.\kuroshio_1993.nc'

# Plot domain
domain = [115, 132, 15, 32]

# Plot first depth layer
dep = 1

# Physical depth values
physical_depths = [0.49, 1.54, 2.65, 3.82, 5.08, 6.44, 7.93, 9.57, 11.40, 13.47,
                   15.81, 18.50, 21.60, 25.21, 29.44, 34.43, 40.34, 47.37, 55.76, 65.81,
                   77.85, 92.33, 109.73, 130.67, 155.85, 186.13, 222.48, 266.04, 318.13, 380.21]

print(f"Reading: {example_file}")
print(f"Plotting Day 001, Depth Layer {dep}...")

# ================= Read data with netCDF4 =================
ds = nc.Dataset(example_file, 'r')

# Access the group
day_group = ds.groups['day001']
depth_group = day_group.groups[f'depth{dep:02d}']

# Read data
main_lon = depth_group.variables['main_axis_lon'][:]
main_lat = depth_group.variables['main_axis_lat'][:]

left_lon = depth_group.variables['left_bdy_lon'][:] if 'left_bdy_lon' in depth_group.variables else None
left_lat = depth_group.variables['left_bdy_lat'][:] if 'left_bdy_lat' in depth_group.variables else None
right_lon = depth_group.variables['right_bdy_lon'][:] if 'right_bdy_lon' in depth_group.variables else None
right_lat = depth_group.variables['right_bdy_lat'][:] if 'right_bdy_lat' in depth_group.variables else None

ds.close()

print(f"  Main axis: {len(main_lon)} points")
if left_lon is not None:
    print(f"  Left boundary: {len(left_lon)} points")
if right_lon is not None:
    print(f"  Right boundary: {len(right_lon)} points")

# ================= Create simple plot (no map background) =================
fig, ax = plt.subplots(figsize=(12, 8))

# Plot main axis (solid line)
if len(main_lon) > 0:
    h_main, = ax.plot(main_lon, main_lat, '-',
                      linewidth=2.5, color='blue',
                      label=f'Main Axis ({physical_depths[dep-1]:.2f} m)')

# Plot left boundary (dashed line)
if left_lon is not None and len(left_lon) > 0:
    h_left, = ax.plot(left_lon, left_lat, '--',
                      linewidth=2, color='red',
                      label=f'Left Boundary ({physical_depths[dep-1]:.2f} m)')

# Plot right boundary (dashed line)
if right_lon is not None and len(right_lon) > 0:
    h_right, = ax.plot(right_lon, right_lat, '--',
                       linewidth=2, color='green',
                       label=f'Right Boundary ({physical_depths[dep-1]:.2f} m)')

# Set axis limits
ax.set_xlim(domain[0], domain[1])
ax.set_ylim(domain[2], domain[3])

# Add labels with larger font
ax.set_xlabel('Longitude (°E)', fontsize=12)
ax.set_ylabel('Latitude (°N)', fontsize=12)

# Add grid
ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)

# Add legend
ax.legend(loc='lower right', fontsize=11, framealpha=0.9)

# Add title
ax.set_title(f'Kuroshio Axis - Day 001, Depth {dep} ({physical_depths[dep-1]:.2f}m), 1993',
             fontsize=14, fontweight='bold')


# Add minor grid
ax.minorticks_on()
ax.grid(True, which='minor', linestyle=':', alpha=0.2)

plt.tight_layout()
plt.show()

print('Plot completed!')