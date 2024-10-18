# Second plot: Throughput (Kops/s) as bars
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["font.family"] = "Times New Roman"

# Data for Throughput (Kops/s)
configurations = ['10', '20', '40', '80', '100']
throughput_data = {
    '100W': [30.77, 40.37, 55.76, 72.57, 81.61],
    '90W10R': [19.73, 23.8, 24.82, 26.53, 24.97],
    '70W30R': [21.38, 23.19, 23.9, 26.94, 24.18]
}

# Color scheme
bar_colors = ['#299D8F', '#E9C46A', '#D87659']  # Matching bar colors
width = 0.25  # Width of bars
bar_offset = np.arange(len(configurations))  # X locations for bar groups

# Plot: Throughput (Kops/s)
fig2, ax2 = plt.subplots(figsize=(8.3, 4.9))  # 4:3 aspect ratio
for idx, (workload, throughput) in enumerate(throughput_data.items()):
    ax2.bar(bar_offset + idx * width, throughput, width, label=workload, color=bar_colors[idx])

# Setting axis labels for Throughput
ax2.set_xlabel('L0-CC Soft Threshold', fontsize=38)
ax2.set_ylabel('Throughput (Kops/s)', fontsize=35)

# Set y-axis limit for better visibility
ax2.set_ylim(0, 100)

# Customizing tick labels and their sizes
ax2.set_xticks(bar_offset + width)
ax2.set_xticklabels(configurations, fontsize=30)
ax2.yaxis.set_tick_params(labelsize=30)
ax2.xaxis.set_tick_params(labelsize=30)

# Adding the legend for Throughput
ax2.legend(fontsize=23, title_fontsize=25, loc='upper left', ncol=3, columnspacing=0.5, frameon=False)

# Adjusting the line width of axis spines
for ax in [ax2]:
    ax.spines['top'].set_linewidth(2)
    ax.spines['right'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()

# Save Throughput figure as PDF
pdf_path_throughput = 'F2C6-L0CC-Throughput-bars.png'
plt.savefig(pdf_path_throughput, format='png')

# Show the plot
plt.show()

pdf_path_throughput
