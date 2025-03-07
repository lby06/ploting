import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# 添加搜索路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from optimal_plan import optimal_plan

def plot_storage_soc(m, city_name):
    # 创建保存结果的文件夹
    output_folder = os.path.join(os.getcwd(), 'storage_soc_plots')
    os.makedirs(output_folder, exist_ok=True)

    # 提取储能设备的SOC数据
    cold_storage_soc = {t: m.storage_soc[2, t]() for t in m.t_8760}
    heat_storage_soc = {t: m.storage_soc[1, t]() for t in m.t_8760}

    # 将SOC数据转换为DataFrame
    cold_storage_df = pd.DataFrame(list(cold_storage_soc.items()), columns=['Time', 'SOC'])
    heat_storage_df = pd.DataFrame(list(heat_storage_soc.items()), columns=['Time', 'SOC'])

    # 绘制冷储能设备的SOC变化
    plt.figure(figsize=(12, 6))
    for day in range(364):
        daily_cold_soc = cold_storage_df[cold_storage_df['Time'].between(day * 24, (day + 1) * 24)]
        plt.plot(range(25), daily_cold_soc['SOC'], alpha=0.1, color='blue')
    plt.xlabel('Hour of the Day')
    plt.ylabel('SOC (Cold Storage)')
    plt.title(f'Cold Storage SOC Variation Over 24 Hours - {city_name}')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'/Users/liuboyuan/Desktop/ploting/plots/storage_soc_plots/{city_name}_cold_storage_soc.png')
    plt.close()

    # 绘制热储能设备的SOC变化
    plt.figure(figsize=(12, 6))
    for day in range(364):
        daily_heat_soc = heat_storage_df[heat_storage_df['Time'].between(day * 24, (day + 1) * 24)]
        plt.plot(range(25), daily_heat_soc['SOC'], alpha=0.1, color='red')
    plt.xlabel('Hour of the Day')
    plt.ylabel('SOC (Heat Storage)')
    plt.title(f'Heat Storage SOC Variation Over 24 Hours - {city_name}')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'{city_name}_heat_storage_soc.png'))
    plt.close()

    print(f'Saved SOC plots for {city_name}')

if __name__ == '__main__':
    city_code = 1  # 北京的城市代码
    city_name = "Beijing"
    m = optimal_plan(city_code, 0, 3.8)
    plot_storage_soc(m, city_name)