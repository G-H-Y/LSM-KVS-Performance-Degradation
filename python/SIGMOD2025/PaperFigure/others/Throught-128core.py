import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data for Throughput (Kops/s) from the new image
configurations = ['4', '8', '16', '24', '32', '48', '64', '128']
# throughput_data = {
#     '100W': [32.36, 32.46, 35.28, 36.59, 33.27, 32.79, 32.41, 32.58],
#     '90W10R': [24.52, 25.42, 24.72, 25.10, 25.74, 25.42, 24.21, 23.96],
#     '70W30R': [24.76, 24.21, 23.93, 24.50, 24.96, 24.43, 24.59, 24.02],
#     '50W50R': [26.15, 25.80, 26.60, 26.86, 26.94, 27.58, 27.25, 27.53],
#     '30W70R': [30.17, 29.44, 29.73, 30.06, 30.84, 30.65, 30.21, 31.65],
#     '10W90R': [45.47, 46.56, 43.36, 46.04, 45.83, 45.92, 45.63, 46.91]
# }

throughput_data = {
    '100W': [44.38, 46.52, 43.92, 41.19, 40.7, 40.04, 39.27, 39.88],
    '90W10R': [34.1, 25.82, 27.87, 28.4, 30.19, 29.65, 28.22, 29.29],
    '70W30R': [29.7, 26.72, 25.12, 25.97, 25.62, 26.03, 25.58, 25.3],
    '50W50R': [30.15, 25.32, 25.08, 25.65, 23.92, 25.57, 25.94, 24.4],
    '30W70R': [33.96, 29.35, 30.02, 28.71, 28.83, 28.55, 29.6, 29.08],
    '10W90R': [45.63, 43.34, 43.32, 43.5, 43.26, 42.6, 43.1, 43.07]
}
# Updated markers and colors as per the user's request
markers = {
    '100W': 'v',   # Triangle down (new marker)
    '90W10R': 'o',  # Circle
    '70W30R': 'x',  # Cross
    '50W50R': 's',  # Square
    '30W70R': 'D',  # Diamond
    '10W90R': '^'   # Triangle up
}

colors = {
    '100W': '#8c564b',  # Brown for 100W
    '90W10R': '#1f77b4',  # Blue
    '70W30R': '#ff7f0e',  # Orange
    '50W50R': '#2ca02c',  # Green
    '30W70R': '#d62728',  # Red
    '10W90R': '#9467bd'   # Purple
}

marker_size = 8  # Set a larger marker size

# Create the figure and axis with a 4:3 aspect ratio
fig, ax = plt.subplots(figsize=(8, 6))  # 4:3 aspect ratio

# Plot each workload type as a line plot with different markers and colors
for workload, throughput in throughput_data.items():
    ax.plot(configurations, throughput, marker=markers[workload], color=colors[workload], label=workload, markersize=marker_size)

# Setting the axis labels with larger font sizes
ax.set_xlabel('Number of Background Threads', fontsize=35)
ax.set_ylabel('Throughput (Kops/s)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)

# Set y-axis limit
ax.set_ylim(20, 55)

# Adding the legend with a larger font size, positioned in the upper left
ax.legend(ncol=3, fontsize=18.8, title_fontsize=25, loc='upper left')

# Save the plot as a PDF with 4:3 aspect ratio
plt.tight_layout()
plt.savefig('Throughput-BKThreads-128core.pdf', format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()

