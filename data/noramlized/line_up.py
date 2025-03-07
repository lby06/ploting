import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_sorted_loads(city_map):
    # 创建保存结果的文件夹
    output_folder = os.path.join(os.getcwd(), 'sorted_loads_plots')
    os.makedirs(output_folder, exist_ok=True)

    # 定义颜色列表
    colors = ['red', 'blue', 'green', 'orange']

    # 绘制电负荷排序图
    plt.figure(figsize=(12, 6))
    for i, (city_code, city_name) in enumerate(city_map.items()):
        file_path = f'/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_name}_data_normalized.csv'
        df = pd.read_csv(file_path)
        df_sorted_elec = df.sort_values(by='elec_load(MW)', ascending=False).reset_index(drop=True)
        plt.plot(df_sorted_elec['elec_load(MW)'], label=f'{city_name} Elec Load (MW)', color=colors[i])
    plt.xlabel('Time')
    plt.ylabel('Electric Load (MW)')
    plt.title('Sorted Electric Load for All Cities')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'sorted_electric_load.png'))
    plt.close()

    # 绘制热负荷排序图
    plt.figure(figsize=(12, 6))
    for i, (city_code, city_name) in enumerate(city_map.items()):
        file_path = f'/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_name}_data_normalized.csv'
        df = pd.read_csv(file_path)
        df_sorted_heat = df.sort_values(by='heating_load(MW)', ascending=False).reset_index(drop=True)
        plt.plot(df_sorted_heat['heating_load(MW)'], label=f'{city_name} Heating Load (MW)', color=colors[i])
    plt.xlabel('Time')
    plt.ylabel('Heating Load (MW)')
    plt.title('Sorted Heating Load for All Cities')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'sorted_heating_load.png'))
    plt.close()

    # 绘制冷负荷排序图
    plt.figure(figsize=(12, 6))
    for i, (city_code, city_name) in enumerate(city_map.items()):
        file_path = f'/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_name}_data_normalized.csv'
        df = pd.read_csv(file_path)
        df_sorted_cold = df.sort_values(by='cooling_load(MW)', ascending=False).reset_index(drop=True)
        plt.plot(df_sorted_cold['cooling_load(MW)'], label=f'{city_name} Cooling Load (MW)', color=colors[i])
    plt.xlabel('Time')
    plt.ylabel('Cooling Load (MW)')
    plt.title('Sorted Cooling Load for All Cities')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'sorted_cooling_load.png'))
    plt.close()

    # 绘制光伏功率排序图
    plt.figure(figsize=(12, 6))
    for i, (city_code, city_name) in enumerate(city_map.items()):
        file_path = f'/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_name}_data_normalized.csv'
        df = pd.read_csv(file_path)
        df_sorted_pv = df.sort_values(by='PV', ascending=False).reset_index(drop=True)
        plt.plot(df_sorted_pv['PV'], label=f'{city_name} PV Power', color=colors[i])
    plt.xlabel('Time')
    plt.ylabel('PV Power')
    plt.title('Sorted PV Power for All Cities')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'sorted_pv_power.png'))
    plt.close()

    print('Saved sorted load plots for all cities')

if __name__ == '__main__':
    city_map = {1: "Beijing", 2: "Guangzhou", 3: "Wuhan", 4: "Wulumuqi"}
    plot_sorted_loads(city_map)