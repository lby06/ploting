import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))



import matplotlib.pyplot as plt
import numpy as np
from optimal_plan import optimal_plan

def get_total_cost_excluding_carbon(model):
    total_cost = model.total_cost()
    carbon_cost = model.carbon_cost()
    return total_cost - carbon_cost

# 设置pv_space_values和carbon_price_values的值
pv_space_values = np.linspace(3.8, 6, 10)
carbon_price_values =[0,100,400,700,900]

city_map = {
    1: "Beijing",
    2: "Guangzhou",
    3: "Wuhan",
    4: "Wulumuqi"
}

cities = [1, 2, 3, 4]  # 假设城市代码为1, 2, 3, 4

# # 作图：4个城市 x轴是pv_space y轴是除去碳成本的总成本
plt.figure(figsize=(12, 8))
for city_code in cities:
    total_costs = []
    for pv_space in pv_space_values:
        model = optimal_plan(city_code=city_code, carbon_price=0, pv_space=pv_space)
        total_cost = get_total_cost_excluding_carbon(model)
        total_costs.append(total_cost)
    plt.plot(pv_space_values, total_costs, label=city_map[city_code])

plt.xlabel('PV Space')
plt.ylabel('Total Cost Excluding Carbon Cost')
plt.title('Total Cost Excluding Carbon Cost vs PV Space for Different Cities')
plt.legend()
plt.savefig('/Users/liuboyuan/Desktop/ploting/plots/compare_plots/total_cost vs_pv_space.png')
plt.close()

# 作图：4个城市 x轴是carbon_price y轴是除去碳成本的总成本
plt.figure(figsize=(12, 8))
for city_code in cities:
    total_costs = []
    for carbon_price in carbon_price_values:
        model = optimal_plan(city_code=city_code, carbon_price=carbon_price, pv_space=3.8)
        total_cost = get_total_cost_excluding_carbon(model)
        total_costs.append(total_cost)
    plt.plot(carbon_price_values, total_costs, label=city_map[city_code])

plt.xlabel('Carbon Price')
plt.ylabel('Total Cost Excluding Carbon Cost')
plt.title('Total Cost Excluding Carbon Cost vs Carbon Price for Different Cities')
plt.legend()
plt.savefig('/Users/liuboyuan/Desktop/ploting/plots/compare_plots/total_cost vs_carbon_price.png')
plt.close()