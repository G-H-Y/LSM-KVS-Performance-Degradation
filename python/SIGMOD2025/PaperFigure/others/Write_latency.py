import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data for Write Latency
configurations = ['4', '8', '16', '24', '32', '48', '64', '128']
write_latencies = {
    '100W': [3059, 3054, 2814, 2791, 2985, 3028, 3061, 3042],
    '90W10R': [3540, 3277, 2289, 1997, 2050, 1720, 1789, 2064],
    '70W30R': [2637, 1159, 371, 485, 829, 716, 809, 891],
    '50W50R': [119, 139, 205, 159, 164, 178, 174, 186],
    '30W70R': [87, 97, 106, 100, 108, 97, 101, 140],
    '10W90R': [53, 58, 57, 56, 53, 54, 55, 56]
}

# Define markers and colors to match your updated style
markers = {
    '100W': 'v',   # Triangle down
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
for workload, latency in write_latencies.items():
    ax.plot(configurations, latency, marker=markers[workload], color=colors[workload], label=workload, markersize=marker_size)

# Setting the axis labels with larger font sizes
ax.set_xlabel('Number of Background Threads', fontsize=35)
ax.set_ylabel('Write Latency (us)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)

# Set y-axis limit to 4500
ax.set_ylim(0, 4500)

# Adding the legend with a larger font size, positioned in the upper left
ax.legend(ncol=3, fontsize=18.3, title_fontsize=25, loc='upper left')

# Save the plot as a PDF with 4:3 aspect ratio
plt.tight_layout()
plt.savefig('WriteLatency-BKThreads.pdf', format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()

