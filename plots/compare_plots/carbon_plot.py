import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))



import matplotlib.pyplot as plt
import numpy as np
from optimal_plan import optimal_plan

def get_seasonal_heat_storage_capacity(model):
    for device_id, device in enumerate(model.storage_device_list):
        if device.label == "Seasonal_Heat_Storage":
            return model.storage_invest[device_id]()
    return 0

# 设置pv_space_values和carbon_price_values的值
pv_space_values = np.linspace(3.8, 6, 10)
#0,100,400,700,900
carbon_price_values =[0,100,400,700,900]

city_map = {
    1: "Beijing",
    2: "Guangzhou",
    3: "Wuhan",
    4: "Wulumuqi"
}

cities = [1, 2, 3, 4]  # 假设城市代码为1, 2, 3, 4

# # 作图：4个城市 x轴是pv_space y轴是seasonal_heat_storage_capacity
# plt.figure(figsize=(12, 8))
# for city_code in cities:
#     seasonal_heat_storage_capacity = []
#     for pv_space in pv_space_values:
#         model = optimal_plan(city_code=city_code, carbon_price=0, pv_space=pv_space)
#         capacity = get_seasonal_heat_storage_capacity(model)
#         seasonal_heat_storage_capacity.append(capacity)
#     plt.plot(pv_space_values, seasonal_heat_storage_capacity, label=city_map[city_code])

# plt.xlabel('PV Space')
# plt.ylabel('Seasonal Heat Storage Capacity')
# plt.title('Seasonal Heat Storage Capacity vs PV Space for Different Cities')
# plt.legend()
# plt.savefig('/Users/liuboyuan/Desktop/ploting/plots/compare_plots/seasonal_heat_storage_vs_pv_space.png')
# plt.close()

# 作图：4个城市 x轴是carbon_price y轴是seasonal_heat_storage_capacity
plt.figure(figsize=(12, 8))
for city_code in cities:
    seasonal_heat_storage_capacity = []
    for carbon_price in carbon_price_values:
        model = optimal_plan(city_code=city_code, carbon_price=carbon_price, pv_space=3.8)
        capacity = get_seasonal_heat_storage_capacity(model)
        seasonal_heat_storage_capacity.append(capacity)
    plt.plot(carbon_price_values, seasonal_heat_storage_capacity, label=city_map[city_code])

plt.xlabel('Carbon Price')
plt.ylabel('Seasonal Heat Storage Capacity')
plt.title('Seasonal Heat Storage Capacity vs Carbon Price for Different Cities')
plt.legend()
plt.savefig('/Users/liuboyuan/Desktop/ploting/plots/compare_plots/seasonal_heat_storage_vs_carbon_price.png')
plt.close()