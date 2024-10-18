import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data for Throughput (Kops/s) from the new image
configurations = ['4', '8', '16', '24', '32', '48', '64', '128']
# throughput_data = {
#     '100W': [35.58, 34.36, 37.71, 36.92, 37.01, 36.24, 34.81, 34.13],
#     '90W10R': [27.16, 26.64, 27.37, 27.21, 28.13, 27.24, 26.86, 27.02],
#     '70W30R': [27.02, 28.53, 27.02, 27.66, 27.43, 27.04, 27.08, 27.11],
#     '50W50R': [30.57, 29.74, 29.71, 29.52, 29.41, 28.66, 30.36, 29.98],
#     '30W70R': [33.9, 34.13, 32.56, 32.28, 31.22, 33.03, 35.21, 35.48],
#     '10W90R': [47.94, 48.08, 49.81, 45.68, 48.83, 50.02, 48.77, 48.6]
# }
throughput_data = {
    '100W': [26.96, 35.86, 41.46, 40.46, 40.23, 38.12, 36.98, 37.66],
    '90W10R': [24.61, 25.62, 28.44, 29.01, 25.77, 27.36, 26.61, 27.19],
    '70W30R': [23.04, 27.27, 27.43, 27.54, 26.49, 26.44, 25.95, 27.39],
    '50W50R': [30.46, 27.33, 26.13, 29.44, 28.16, 28.41, 29.1, 27.52],
    '30W70R': [33.37, 33.25, 32.68, 33.82, 28.34, 32.99, 30.9, 28.66],
    '10W90R': [40.05, 45.22, 45.68, 34.26, 32.59, 45.33, 42.5, 39.55]
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
plt.savefig('Throughput-BKThreads-8core.pdf', format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()

