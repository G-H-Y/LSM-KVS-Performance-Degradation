import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
# Updated Data for Throughput (Kops/s) from the extracted data
# Updated Data for Stall Duration from the extracted data
configurations = ['2', '8', '16', '32']
stall_duration_data = {
    # '100W': [586, 365, 27, 130],
    # '90W10R': [351, 143, 149, 140],
    # '70W30R': [62, 22, 35, 14]
'100W': [591, 465, 496, 410],
    '90W10R': [337, 187, 175, 132],
    '70W30R': [31, 45, 40, 52]
}

# Plot configuration using previous color and marker settings
markers = {
    '100W': 'v',   # Triangle down
    '90W10R': 'o',  # Circle
    '70W30R': 'x',  # Cross
}

colors = {
    '100W': '#8c564b',  # Brown for 100W
    '90W10R': '#1f77b4',  # Blue
    '70W30R': '#ff7f0e',  # Orange
}

marker_size = 8  # Set a larger marker size

# Create the figure and axis with a 4:3 aspect ratio
fig, ax = plt.subplots(figsize=(8, 6))  # 4:3 aspect ratio

# Plot each workload type as a line plot with different markers and colors
for workload, duration in stall_duration_data.items():
    ax.plot(configurations, duration, marker=markers[workload], color=colors[workload], label=workload, markersize=marker_size, linewidth=2.5)

# Setting the axis labels with larger font sizes
ax.set_xlabel('Number of MemTables', fontsize=35)
ax.set_ylabel('Write Stall Duration (s)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)

# Set y-axis limit for better visibility
ax.set_ylim(0, 680)

# Adding the legend with a larger font size, positioned in the upper right
ax.legend(ncol=1, fontsize=18.8, title_fontsize=25, loc='upper right')

# Adjusting the line width of the axis spines for both x and y axes
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()
pdf_path = 'F32C96-WSDuration-MT-CC.pdf'
plt.savefig(pdf_path, format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()

pdf_path
