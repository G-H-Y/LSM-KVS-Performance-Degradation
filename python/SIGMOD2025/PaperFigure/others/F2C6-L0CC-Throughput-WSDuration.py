import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

# Updated data for Throughput (Kops/s) and Stall Duration (s)
configurations = ['10', '20', '40', '80', '100']
throughput_data = {
    '100W': [30.77, 40.37, 55.76, 72.57, 81.61],
    '90W10R': [19.73, 23.8, 24.82, 26.53, 24.97],
    '70W30R': [21.38, 23.19, 23.9, 26.94, 24.18]
}
stall_duration_data = {
    '100W': [317, 251, 208, 143, 75],
    '90W10R': [283, 170, 0, 0, 0],
    '70W30R': [158, 0, 0, 0, 0]
}

# Marker and color settings (updated as per the new color scheme)
markers = {
    '100W': 'v',   # Triangle down
    '90W10R': 'o',  # Circle
    '70W30R': 'x',  # Cross
}

# Corrected color scheme
colors = {
    '100W': '#299D8F',  # Greenish
    '90W10R': '#E9C46A',  # Yellowish
    '70W30R': '#D87659',  # Reddish-Orange
}

bar_colors = ['#299D8F', '#E9C46A', '#D87659']  # Matching bar colors for stall duration
marker_size = 8  # Set marker size

# Create the figure and axis
fig, ax1 = plt.subplots(figsize=(9.5, 6))  # 4:3 aspect ratio

# Plot Stall Duration as bars
width = 0.25  # Width of bars
bar_offset = np.arange(len(configurations))  # X locations for bar groups
for idx, (workload, duration) in enumerate(stall_duration_data.items()):
    ax1.bar(bar_offset + idx * width, duration, width, label=workload + ' (Stall)', color=bar_colors[idx])

# Create the secondary y-axis for throughput and plot throughput on top of the bars
ax2 = ax1.twinx()  # Secondary y-axis sharing the same x-axis
for workload, throughput in throughput_data.items():
    ax2.plot(configurations, throughput, marker=markers[workload], color=colors[workload],
             label=workload + ' (Throughput)', markersize=marker_size, linewidth=2.5)

# Setting the axis labels
ax1.set_xlabel('L0-CC Soft Threshold', fontsize=38)
ax1.set_ylabel('Write Stall Duration (s)', fontsize=38)
ax2.set_ylabel('Throughput (Kops/s)', fontsize=38)

# Set y-axis limits for better visibility
ax1.set_ylim(0, 1450)  # Keep original scale for stall duration
ax2.set_ylim(0, 85)  # Adjust throughput scale based on new data

# Customizing tick labels and their sizes
ax1.set_xticks(bar_offset + width)
ax1.set_xticklabels(configurations, fontsize=30)
ax1.yaxis.set_tick_params(labelsize=30)
ax2.yaxis.set_tick_params(labelsize=30)
ax1.xaxis.set_tick_params(labelsize=30)

# Adding the legend for both plots, split into two columns and with no border
lines, line_labels = ax2.get_legend_handles_labels()
bars, bar_labels = ax1.get_legend_handles_labels()
ax1.legend(bars + lines, bar_labels + line_labels, fontsize=21, title_fontsize=25, loc='upper left', ncol=2, columnspacing=0.5, frameon=False)

# Adjusting the line width of axis spines
for ax in [ax1, ax2]:
    ax.spines['top'].set_linewidth(2)
    ax.spines['right'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()

# Save the combined plot as a PDF
pdf_path = 'F2C6-L0CC-Throughput-WSDuration.pdf'
plt.savefig(pdf_path, format='pdf')

# Show the plot
plt.show()

pdf_path
