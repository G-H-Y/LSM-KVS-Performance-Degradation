import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated Data for Stall Duration from the extracted data
configurations = ['10', '20', '40', '80', '100']
stall_duration_data = {
    '100W': [317, 251, 208, 143, 75],
    '90W10R': [283, 170, 0, 0, 0],
    '70W30R': [158, 0, 0, 0, 0]
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

# Plot each workload type as a line plot with different markers, colors, and thicker lines
for workload, duration in stall_duration_data.items():
    ax.plot(configurations, duration, marker=markers[workload], color=colors[workload],
            label=workload, markersize=marker_size, linewidth=2.5)  # Line width increased

# Setting the axis labels with larger font sizes
ax.set_xlabel('L0-CC Soft Threshold', fontsize=35)
ax.set_ylabel('Write Stall Duration (s)', fontsize=35)
ax.set_xticks(np.arange(len(configurations)))  # Ensures that only the specific tick values are shown
ax.set_xticklabels(configurations, fontsize=25)
ax.yaxis.set_tick_params(labelsize=25, width=2)
ax.xaxis.set_tick_params(labelsize=25, width=2)

# Set y-axis limit for better visibility
ax.set_ylim(0, 330)

# Adding the legend with a larger font size, positioned in the upper right
ax.legend(ncol=1, fontsize=18.8, title_fontsize=25, loc='upper right')

# Adjusting the line width of the axis spines for both x and y axes
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()

# Save the plot as a PDF with the specified filename
pdf_path = 'F2C6-WSDuration-L0CC.pdf'
plt.savefig(pdf_path, format='pdf')

# Show the plot
plt.show()

pdf_path
