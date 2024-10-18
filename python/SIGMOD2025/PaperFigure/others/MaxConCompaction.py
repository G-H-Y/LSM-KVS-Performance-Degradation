import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data for Maximum Concurrent Compaction
configurations = ['4', '8', '16', '24', '32', '48', '64', '128']
max_concurrent_compaction = {
        '100W': [3, 5, 11, 15, 20, 22, 25, 25],
    '90W10R': [3, 4, 10, 15, 20, 22, 25, 25],
    '70W30R': [3, 4, 8, 8, 9, 9, 11, 11],
    '50W50R': [3, 4, 6, 6, 6, 7, 6, 7],
    '30W70R': [3, 3, 6, 7, 6, 7, 6, 6],
    '10W90R': [2, 3, 3, 2, 2, 3, 3, 3]
}

# Define markers and colors to match your style
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
for workload, compaction in max_concurrent_compaction.items():
    ax.plot(configurations, compaction, marker=markers[workload], color=colors[workload], label=workload, markersize=marker_size)

# Setting the axis labels with larger font sizes
ax.set_xlabel('Number of Background Threads', fontsize=35)
ax.set_ylabel('Concurrent Compaction #', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)

ax.set_ylim(0, 33)

# Adding the legend with a larger font size, positioned in the upper left
ax.legend(ncol=3, fontsize=18.6, title_fontsize=25, loc='upper left')

# Save the plot as a PDF with 4:3 aspect ratio
plt.tight_layout()
plt.savefig('MaxConCompaction-BKThreads.pdf', format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()
