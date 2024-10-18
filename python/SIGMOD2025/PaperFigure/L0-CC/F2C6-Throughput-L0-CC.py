import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data for Throughput (Kops/s) from the new extracted data
configurations = ['10', '20', '40', '80', '100']
throughput_data = {
    '100W': [30.77, 40.37, 55.76, 72.57, 81.61],
    '90W10R': [19.73, 23.8, 24.82, 26.53, 24.97],
    '70W30R': [21.38, 23.19, 23.9, 26.94, 24.18]
}

# Updated markers and colors as per the user's request
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

# Plot each workload type as a line plot with different markers, colors, and thicker lines
for workload, throughput in throughput_data.items():
    ax.plot(configurations, throughput, marker=markers[workload], color=colors[workload],
            label=workload, markersize=marker_size, linewidth=2.5)

# Setting the axis labels with larger font sizes
ax.set_xlabel('L0-CC Soft Threshold', fontsize=35)
ax.set_ylabel('Throughput (Kops/s)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.xaxis.set_tick_params(labelsize=25)

# Set y-axis limit for better visibility
ax.set_ylim(15, 85)

# Adding the legend with a larger font size, positioned in the upper left
ax.legend(ncol=1, fontsize=18.8, title_fontsize=25, loc='upper left')

# Adjusting the line width of the axis spines for both x and y axes
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()

# Save the plot as a PDF with the specified filename
pdf_path = 'F2C6-Throughput-L0-CC.pdf'
plt.savefig(pdf_path, format='pdf')

# Show the plot
plt.show()

pdf_path
