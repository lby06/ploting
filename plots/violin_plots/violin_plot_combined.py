import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))



from optimal_plan import optimal_plan as optimal_plan_with_ss
from optimal_plan_no_ss import optimal_plan as optimal_plan_no_ss
import numpy as np
import matplotlib.pyplot as plt

def hour_cost(model):
    hour_costs = []
    for t in range(8760):
        hour_cost = 0
        hour_cost += model.elec_price[t] * model.buy_energy["elec", t]() / 10000
        hour_cost += model.gas_price[t] * model.buy_energy["gas", t]() / 10000
        hour_cost += model.invest_cost() / 10000 / 8760
        hour_costs.append(hour_cost)
    return hour_costs

city_map = {
    1: "Beijing",
    2: "Guangzhou",
    3: "Wuhan",
    4: "Wulumuqi"
}

cities = [1, 2, 3, 4]  # 假设城市代码为1, 2, 3, 4
#carbon_prices = [100, 400, 700, 900]  # 碳价格
carbon_prices = [0]

# 生成小提琴图
for carbon_price in carbon_prices:
    plt.figure(figsize=(12, 8))
    
    for i, city_code in enumerate(cities):
        # 有季节性储能的情景
        model_with_ss = optimal_plan_with_ss(city_code=city_code, carbon_price=carbon_price, pv_space=3.8)
        costs_with_ss = hour_cost(model_with_ss)
        
        # 无季节性储能的情景
        model_no_ss = optimal_plan_no_ss(city_code=city_code, carbon_price=carbon_price, pv_space=3.8)
        costs_no_ss = hour_cost(model_no_ss)
        
        # 绘制小提琴图
        parts_with_ss = plt.violinplot([costs_with_ss], positions=[i * 2 - 0.3], showmeans=False, showmedians=True)
        parts_no_ss = plt.violinplot([costs_no_ss], positions=[i * 2 + 0.3], showmeans=False, showmedians=True)
        
        # 设置颜色
        for pc in parts_with_ss['bodies']:
            pc.set_facecolor('blue')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)
        for pc in parts_no_ss['bodies']:
            pc.set_facecolor('red')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)

    plt.xticks(np.arange(0, len(cities) * 2, 2), [city_map[city_code] for city_code in cities])
    plt.xlabel('City')
    plt.ylabel('Hourly Cost (million RMB)')
    plt.title(f'Hourly Cost Distribution for Different Cities with and without Seasonal Storage (Carbon Price: {carbon_price})')
    
    # 创建自定义图例
    blue_patch = plt.Line2D([0], [0], color='blue', lw=4, label='With Seasonal Storage')
    red_patch = plt.Line2D([0], [0], color='red', lw=4, label='Without Seasonal Storage')
    plt.legend(handles=[blue_patch, red_patch])

    plt.savefig(f'/Users/liuboyuan/Desktop/ploting/plots/violin_plots/hourly_cost_violin_plot_comparison_carbon_price_{carbon_price}.png')
    plt.close()