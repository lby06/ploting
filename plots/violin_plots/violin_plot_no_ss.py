import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from optimal_plan_no_ss import optimal_plan
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

def group_by_month(hour_costs):
    month_costs = [[] for _ in range(12)]
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    start_hour = 0
    for month, days in enumerate(days_in_month):
        end_hour = start_hour + days * 24
        month_costs[month] = hour_costs[start_hour:end_hour]
        start_hour = end_hour
    return month_costs

city_map = {
    1: "Beijing",
    2: "Guangzhou",
    3: "Wuhan",
    4: "Wulumuqi"
}

cities = [1, 2, 3, 4]  # 假设城市代码为1, 2, 3, 4

# 生成小提琴图
for city_code in cities:
    plt.figure(figsize=(12, 8))
    model = optimal_plan(city_code=city_code, carbon_price=0, pv_space=3.8)
    costs = hour_cost(model)
    month_costs = group_by_month(costs)
    
    plt.violinplot(month_costs, showmeans=False, showmedians=True)
    plt.xticks(range(1, 13), [f'Month {i}' for i in range(1, 13)])
    plt.xlabel('Month')
    plt.ylabel('Hourly Cost (million RMB)')
    plt.title(f'Hourly Cost Distribution by Month for {city_map[city_code]}')
    plt.savefig(f'/Users/liuboyuan/Desktop/ploting/plots/violin_plots/hourly_cost_violin_plot_{city_map[city_code]}_no_ss.png')
    plt.close()