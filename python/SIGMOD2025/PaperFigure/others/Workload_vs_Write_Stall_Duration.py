import matplotlib.pyplot as plt
import numpy as np

# Set the font to Times New Roman for all text elements
plt.rcParams["font.family"] = "Times New Roman"

# Data from the table
cpu_cores = [8, 16, 32, 64, 128]
workloads = ['100W0R', '90W10R', '70W30R']

# Transposed data to match workloads with CPU cores
data_corrected = np.array([
    [478, 446, 476, 498, 499],  # 100W0R
    [308, 346, 375, 401, 410],  # 90W10R
    [102,  90, 124, 161, 182]   # 70W30R
])

# Define the updated color palette
colors_updated = ['#e05b3d', '#c8e5ed', '#344e99', '#f5b46f', '#73a1c3']

# Define bar width and positions
bar_width = 0.15
x = np.arange(len(workloads))

# Plotting the data with the updated color palette and larger fonts
fig, ax = plt.subplots(figsize=(10, 6))
for i in range(len(cpu_cores)):
    ax.bar(x + i * bar_width, data_corrected[:, i], width=bar_width, color=colors_updated[i], label=f'{cpu_cores[i]} cores')

# Adding labels and title with larger font sizes
ax.set_xlabel('Workload', fontsize=25)
ax.set_ylabel('Write Stall Duration (s)', fontsize=25)
ax.set_xticks(x + 2 * bar_width)
ax.set_xticklabels(workloads, fontsize=20)
ax.yaxis.set_tick_params(labelsize=20)

# Adding legend with larger font size
ax.legend(title='CPU Cores', title_fontsize=22, fontsize=20)

# Save the plot as a PDF file
plt.tight_layout()
plt.savefig('Workload_vs_Write_Stall_Duration.pdf', format='pdf')
