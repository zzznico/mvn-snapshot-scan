import os

# 定义目标目录和输出文件名
directory = '/snapshot'
output_filename = 'merged_unique_lines.txt'

# 初始化一个空集合用于存储唯一行
unique_lines = set()

# 遍历目录及其子目录下的所有txt文件
for root, dirs, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.txt'):
            filepath = os.path.join(root, filename)
            #print(filepath)
            # 打开每个txt文件并读取内容
            with open(filepath, 'r') as file:
                for line in file:
                    # 去除行尾的换行符并添加到集合中
                    unique_lines.add(line.strip())

print(unique_lines)
# 将所有唯一行写入新的txt文件
with open(os.path.join(directory, output_filename), 'w') as output_file:
    for line in unique_lines:
        output_file.write(f'{line}\n')