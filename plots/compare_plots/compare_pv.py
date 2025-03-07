import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import matplotlib.pyplot as plt
from optimal_plan import optimal_plan

def calculate_daily_difference(model):
    # 获取电负载和PV发电量
    elec_load = [model.elec_load[t] for t in model.t_8760]
    pv_generation = [model.solar_Area[0]() * model.solar_device_list[0].efficiency[0] * model.pv_I[t] * model.solar_device_list[0].area_rate for t in model.t_8760]

    # 创建DataFrame
    data = {'elec_load': elec_load, 'pv_generation': pv_generation}
    df = pd.DataFrame(data)

    # 将时间索引设置为每小时
    df.index = pd.date_range(start='1/1/2023', periods=len(df), freq='H')

    # 按天汇总数据
    daily_load = df['elec_load'].resample('D').sum()
    daily_pv = df['pv_generation'].resample('D').sum()

    # 计算每天的差值
    daily_difference = daily_pv - daily_load
    return daily_difference

def plot_daily_difference(daily_difference):
    plt.figure(figsize=(10, 6))
    daily_difference.plot()
    plt.title('Daily PV Production - Electric Load')
    plt.xlabel('Date')
    plt.ylabel('Difference (MWh)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # 创建模型
    for city_code in [1, 2, 3, 4]:
        model = optimal_plan(city_code=city_code, carbon_price=0, pv_space=3.8)

    # 计算每天的差值
        daily_difference = calculate_daily_difference(model)

    # 绘图
        plot_daily_difference(daily_difference)