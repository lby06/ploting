import matplotlib.pyplot as plt
import pandas as pd
import os

# 读取输入数据
def read_data(city_code):
    # 根据输入的城市代码选择对应的文件名
    city_map = {
        1: "Beijing",
        2: "Guangzhou",
        3: "Wuhan",
        4: "Wulumuqi"
    }
    
    if city_code not in city_map:
        raise ValueError("Invalid city code. Please enter a number between 1 and 4.")
    
    file_name = f"/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_map[city_code]}_data_normalized.csv"
    file_name2 = f"/Users/liuboyuan/Desktop/ploting/normalized_carbon_factors.csv"
    # 读取数据
    df = pd.read_csv(file_name)
    elec_load = df['elec_load(MW)'].tolist()
    heat_load = df['heating_load(MW)'].tolist()
    cold_load = df['cooling_load(MW)'].tolist()
    elec_price = df['elec_price(HKD/MWh)'].tolist()
    gas_price = df['gas_price(HKD/m^3)'].tolist()
    pv_I = df['PV'].tolist() # 归一化的光伏UNits
    
    # 统一燃气的单位从立方米变为MWh
    for i in range(8760):
        gas_price[i] = gas_price[i] * 100
    # 读取碳排放系数
    carbon_df = pd.read_csv(file_name2)
    if city_code == 1:
        elec_carbon = carbon_df['1'].tolist()
    elif city_code == 2:
        elec_carbon = carbon_df['2'].tolist()
    elif city_code == 3:
        elec_carbon = carbon_df['3'].tolist()
    elif city_code == 4:
        elec_carbon = carbon_df['4'].tolist()

    
    return elec_load, heat_load, cold_load, elec_price, gas_price , pv_I , elec_carbon


def plot_energy_data(city_name):
    # 读取数据
    input_file = f'./data/energy_data/{city_name}_energy_data.csv'
    df = pd.read_csv(input_file, index_col=0)

    # 创建输出目录
    output_dir = './plots/energy_plots'
    os.makedirs(output_dir, exist_ok=True)

    # 为每种能源单独绘制图像并保存
    for energy_type in df.columns:
        plt.figure(figsize=(60, 20))  # 调整图像大小
        plt.plot(df.index, df[energy_type], label=energy_type)
        plt.xlabel('Hours')
        plt.ylabel('Energy (MW)')
        plt.title(f'{city_name} - {energy_type.capitalize()} Energy Over 8760 Hours')
        plt.legend()
        plt.grid(True)
        plt.ylim(df[energy_type].min(), df[energy_type].max())
        plt.yticks(range(int(df[energy_type].min()), int(df[energy_type].max()) + 1))
        plt.xticks(range(0, 8760, 24))  # 设置横轴刻度以1小时为单位
        # 保存图像
        image_file = os.path.join(output_dir, f'{city_name}_{energy_type}_energy.png')
        plt.savefig(image_file)
        print(f"Plot for {city_name} - {energy_type} saved to {image_file}")
        plt.close()

if __name__ == '__main__':
    city_names = ["Beijing", "Guangzhou", "Wuhan", "Wulumuqi"]
    
    for city_name in city_names:
        plot_energy_data(city_name)