import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Times New Roman"

# 数据提取自图片
configurations = ['2', '8', '16', '32']
mt_cc = {
    '100W': [245, 11, 0, 0],
    '90W10R': [139, 0, 0, 0],
    '70W30R': [0, 0, 0, 0]
}
lo_cc = {
    '100W': [4, 130, 74, 40],
    '90W10R': [4, 10, 0, 20],
    '70W30R': [0, 0, 0, 0]
}
ec_cc = {
    '100W': [637, 767, 754, 794],
    '90W10R': [663, 735, 685, 721],
    '70W30R': [131, 65, 57, 5]
}

# 定义条形图的位置并增加组之间的间隔
bar_width = 0.2
spacing = 0.3
x = np.arange(len(configurations)) * (bar_width * 3 + spacing)

# 创建图表
fig, ax = plt.subplots(figsize=(9.5, 6))

# 颜色定义
colors = [ '#FA7F6F', '#82B0D2',   '#E7DAD2']  # Example colors for the stacked sections

# 绘制每个工作负载的堆叠柱状图
# 第一组柱子 (100W) 使用 'x' pattern
ax.bar(x - bar_width, mt_cc['100W'], width=bar_width, color=colors[0], hatch='\\', edgecolor='black', linewidth=1, label='MT-CC 100W')
ax.bar(x - bar_width, lo_cc['100W'], width=bar_width, color=colors[1], hatch='\\', edgecolor='black', linewidth=1, bottom=mt_cc['100W'], label='L0-CC 100W')
ax.bar(x - bar_width, ec_cc['100W'], width=bar_width, color=colors[2], hatch='\\', edgecolor='black', linewidth=1, bottom=np.array(mt_cc['100W']) + np.array(lo_cc['100W']), label='EC-CC 100W')

# 第二组柱子 (90W10R) 使用 'o' pattern
ax.bar(x, mt_cc['90W10R'], width=bar_width, color=colors[0], hatch='.', edgecolor='black', linewidth=1, label='MT-CC 90W10R')
ax.bar(x, lo_cc['90W10R'], width=bar_width, color=colors[1], hatch='.', edgecolor='black', linewidth=1, bottom=mt_cc['90W10R'], label='L0-CC 90W10R')
ax.bar(x, ec_cc['90W10R'], width=bar_width, color=colors[2], hatch='.', edgecolor='black', linewidth=1, bottom=np.array(mt_cc['90W10R']) + np.array(lo_cc['90W10R']), label='EC-CC 90W10R')

# 第三组柱子 (70W30R) 使用 '/' pattern
ax.bar(x + bar_width, mt_cc['70W30R'], width=bar_width, color=colors[0], hatch='/', edgecolor='black', linewidth=1, label='MT-CC 70W30R')
ax.bar(x + bar_width, lo_cc['70W30R'], width=bar_width, color=colors[1], hatch='/', edgecolor='black', linewidth=1, bottom=mt_cc['70W30R'], label='L0-CC 70W30R')
ax.bar(x + bar_width, ec_cc['70W30R'], width=bar_width, color=colors[2], hatch='/', edgecolor='black', linewidth=1, bottom=np.array(mt_cc['70W30R']) + np.array(lo_cc['70W30R']), label='EC-CC 70W30R')

# 设置标签和标题
ax.set_xlabel('Number of Memtables', fontsize=38)
ax.set_ylabel('Write Stall Frequency', fontsize=38)
ax.set_xticks(x)
ax.set_xticklabels(configurations, fontsize=26)
ax.tick_params(axis='y', labelsize=26, width=2)

# 设置y轴显示范围
ax.set_ylim(0, 1180)

# 设置坐标轴线条粗细
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

# 将图例放置在图表内部的顶部居中，分为多行
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=17, title_fontsize=18, frameon=False)

plt.tight_layout()

# 保存图表为PDF文件
png_path = 'F2C6-WSFreq-MT-CC.png'
plt.savefig(png_path, format='png')

plt.show()
