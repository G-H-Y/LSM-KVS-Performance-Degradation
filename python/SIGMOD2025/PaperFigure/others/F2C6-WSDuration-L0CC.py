# First plot: Write Stall Duration (s) as bars
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["font.family"] = "Times New Roman"

# Data for Stall Duration (s)
configurations = ['10', '20', '40', '80', '100']
stall_duration_data = {
    '100W': [317, 251, 208, 143, 75],
    '90W10R': [283, 170, 0, 0, 0],
    '70W30R': [158, 0, 0, 0, 0]
}

# Color scheme
bar_colors = ['#299D8F', '#E9C46A', '#D87659']  # Matching bar colors
width = 0.25  # Width of bars
bar_offset = np.arange(len(configurations))  # X locations for bar groups

# Plot: Write Stall Duration
fig1, ax1 = plt.subplots(figsize=(8.3, 4.9))  # 4:3 aspect ratio
for idx, (workload, duration) in enumerate(stall_duration_data.items()):
    ax1.bar(bar_offset + idx * width, duration, width, label=workload, color=bar_colors[idx])

# Setting axis labels for Write Stall Duration
ax1.set_xlabel('L0-CC Soft Threshold', fontsize=38)
ax1.set_ylabel('Duration (s)', fontsize=38)

# Set y-axis limit for better visibility
ax1.set_ylim(0, 400)
# Customizing tick labels and their sizes
ax1.set_xticks(bar_offset + width)
ax1.set_xticklabels(configurations, fontsize=30)
ax1.yaxis.set_tick_params(labelsize=30)
ax1.xaxis.set_tick_params(labelsize=30)

# Adding the legend for Write Stall Duration
ax1.legend(fontsize=23, title_fontsize=25, loc='upper left', ncol=3, columnspacing=0.5, frameon=False)

# Adjusting the line width of axis spines
for ax in [ax1]:
    ax.spines['top'].set_linewidth(2)
    ax.spines['right'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)

plt.tight_layout()

# Save Write Stall Duration figure as PDF
pdf_path_stall_duration = 'F2C6-L0CC-WriteStallDuration-bars.png'
plt.savefig(pdf_path_stall_duration, format='png')

# Show the plot
plt.show()

pdf_path_stall_duration
