import pandas as pd

# 读取 Excel 文件
file_name = f"/Users/liuboyuan/Desktop/ploting/data/carbon_factor/normalized_carbon_factors.xlsx"
df = pd.read_excel(file_name)

# 将 DataFrame 保存为 CSV 文件
csv_file_name = f"/Users/liuboyuan/Desktop/ploting/data/carbon_factor/normalized_carbon_factors.csv"
df.to_csv(csv_file_name, index=False)

print(f"Excel 文件已成功转换为 CSV 文件：{csv_file_name}")