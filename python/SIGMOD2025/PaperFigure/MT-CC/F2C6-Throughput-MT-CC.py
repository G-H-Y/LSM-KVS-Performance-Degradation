import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
# Updated Data for Throughput (Kops/s) from the extracted data
configurations = ['2', '8', '16', '32']
throughput_data = {
'100W': [26.48, 26.5, 27.07, 27.05],
    '90W10R': [22.02, 23.04, 23.09, 23.58],
    '70W30R': [24.81, 24.35, 24.51, 24.72]
}

# Updated markers and colors as per the user's request
markers = {
    '100W': 'v',   # Triangle down (new marker)
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
for workload, throughput in throughput_data.items():
    ax.plot(configurations, throughput, marker=markers[workload], color=colors[workload], label=workload, markersize=marker_size, linewidth=2.5)

# Setting the axis labels with larger font sizes
ax.set_xlabel('Number of MemTables', fontsize=35)
ax.set_ylabel('Throughput (Kops/s)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)

# Set y-axis limit
ax.set_ylim(20, 29.8)

# Adding the legend with a larger font size, positioned in the upper left
ax.legend(ncol=1, fontsize=18.8, title_fontsize=25, loc='upper left')

# Adjusting the line width of the axis spines for both x and y axes
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()
pdf_path = 'F2C6-Throughput-MT-CC.pdf'
plt.savefig(pdf_path, format='pdf')

# Show the plot (not needed if you are running this in a script and saving the figure)
plt.show()

pdf_path
