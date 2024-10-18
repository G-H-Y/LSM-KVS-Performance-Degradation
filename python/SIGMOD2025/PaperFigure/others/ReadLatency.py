import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data
configurations = ['4', '8', '16', '24', '32', '48', '64', '128']
latencies = {
    '90W10R': [8414, 9240, 19230, 21374, 18369, 22980, 26204, 22519],
    '70W30R': [7199, 10937, 12915, 12312, 11269, 11839, 11553, 11668],
    '50W50R': [7454, 7514, 7239, 7220, 7170, 7002, 7091, 7021],
    '30W70R': [4659, 4771, 4724, 4627, 4553, 4591, 4657, 4424],
    '10W90R': [2430, 2370, 2551, 2399, 2409, 2405, 2420, 2354]
}

# Define markers and marker sizes for each workload
markers = {
    '90W10R': 'o',  # Circle
    '70W30R': 'x',  # Cross
    '50W50R': 's',  # Square
    '30W70R': 'D',  # Diamond
    '10W90R': '^'   # Triangle up
}
marker_size = 8  # Set a larger marker size

# Create the figure and axis with a 4:3 aspect ratio
fig, ax = plt.subplots(figsize=(8, 6))  # 4:3 aspect ratio

# Plot each workload type as a line plot with different markers
for workload, latency in latencies.items():
    ax.plot(configurations, latency, marker=markers[workload], label=workload, markersize=marker_size)

# Setting the axis labels with larger font sizes
ax.set_xlabel('Number of Background Threads', fontsize=35)
ax.set_ylabel('Read Latency (us)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)


ax.set_ylim(0, 33500)
# Adding the legend with a larger font size, positioned in the upper left
ax.legend(ncol=3, fontsize=18.2, title_fontsize=25, loc='upper left')

# Save the plot as a PDF with 4:3 aspect ratio
plt.tight_layout()
plt.savefig('ReadLatency-BKThreads.pdf', format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()

