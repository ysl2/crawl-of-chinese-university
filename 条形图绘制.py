import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取 Excel 文件
df = pd.read_excel("中国大学.xlsx")

# 分析每个地区上榜大学的数量，保存在文件中
region_counts = df['所在地区'].value_counts()
region_counts.to_excel("每个地区上榜大学数量.xlsx", index_label="地区")

# 分析前十名的地区的大学数量，绘制柱状图
top_10_regions = region_counts.head(10)

# 解决字体乱码
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'SimHei'

# 创建绘图对象
fig,ax = plt.subplots(figsize=(10, 6))

# 绘制柱状图
x = np.arange(10)
count_y = top_10_regions.values
index_list = top_10_regions.index

ax.tick_params(labelsize=13)
ax.set_ylabel("学校数量")
ax.set_title('前十名的地区的大学数量', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(index_list)
ax.set_ylim([0, 50])
ax.grid()

ax.bar(x, count_y, width=0.5, align='center', color='black', alpha=0.5)

# 在每个柱形上添加数字标签
for x, y in zip(x, count_y):
    ax.text(x, y + 1, y, ha='center', fontsize=13)

# 显示图表
plt.show()
