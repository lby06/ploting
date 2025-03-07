import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import matplotlib.pyplot as plt
from optimal_plan import optimal_plan
import os

def plot_stacked_area(m, city_name):
    # 提取数据
    elec_output = [
        [m.solar_energy["elec", t]() for t in m.t_8760],
        [m.convert_power["CHP_elec", t]() for t in m.t_8760],
        [m.storage_discharge_power[0, t]() for t in m.t_8760]
    ]
    elec_input = [
        [m.convert_power["Electric_Boiler_elec", t]() for t in m.t_8760],
        [m.convert_power["CERG_elec", t]() for t in m.t_8760],
        [m.storage_charge_power[0, t]() for t in m.t_8760],
        [m.elec_load[t] for t in m.t_8760]
    ]
    
    heat_output = [
        [m.solar_energy["heat", t]() for t in m.t_8760],
        [m.convert_power["CHP_heat", t]() for t in m.t_8760],
        [m.convert_power["Gas_Boiler_heat", t]() for t in m.t_8760],
        [m.convert_power["Electric_Boiler_heat", t]() for t in m.t_8760],
        [m.convert_power["Heat_Pump_heat", t]() for t in m.t_8760],
        [m.storage_discharge_power[1, t]() for t in m.t_8760],
        [m.storage_discharge_power[3, t]() for t in m.t_8760]
    ]
    heat_input = [
        [m.convert_power["WARP_heat", t]() for t in m.t_8760],
        [m.storage_charge_power[1, t]() for t in m.t_8760],
        [m.storage_charge_power[3, t]() for t in m.t_8760],
        [m.heat_load[t] for t in m.t_8760]
    ]
    
    cold_output = [
        [m.convert_power["CERG_cold", t]() for t in m.t_8760],
        [m.convert_power["WARP_cold", t]() for t in m.t_8760],
        [m.storage_discharge_power[2, t]() for t in m.t_8760]
    ]
    cold_input = [
        [m.storage_charge_power[2, t]() for t in m.t_8760],
        [m.cold_load[t] for t in m.t_8760]
    ]
    
    # 创建保存图表的文件夹
    os.makedirs('plots/stack_plots', exist_ok=True)
    
    # 绘制电的堆叠折线图
    plt.figure(figsize=(10, 6))
    for data, label in zip(elec_output, ['Solar', 'CHP', 'Storage Output']):
        plt.plot(range(8760), data, label=label)
    for data, label in zip(elec_input, ['Electric Boiler', 'CERG', 'Storage Input', 'Load']):
        plt.plot(range(8760), [-x for x in data], label=label)
    plt.title(f'{city_name} - Electricity')
    plt.legend(loc='upper right')
    plt.savefig(f'plots/stack_plots/{city_name}_electricity.png')
    plt.close()
    
    # 绘制热的堆叠折线图
    plt.figure(figsize=(10, 6))
    for data, label in zip(heat_output, ['Solar', 'CHP', 'Gas Boiler', 'Electric Boiler', 'Heat Pump', 'Storage Output', 'Seasonal Storage Output']):
        plt.plot(range(8760), data, label=label)
    for data, label in zip(heat_input, ['WARP', 'Storage Input', 'Seasonal Storage Input', 'Load']):
        plt.plot(range(8760), [-x for x in data], label=label)
    plt.title(f'{city_name} - Heat')
    plt.legend(loc='upper right')
    plt.savefig(f'plots/stack_plots/{city_name}_heat.png')
    plt.close()
    
    # 绘制冷的堆叠折线图
    plt.figure(figsize=(10, 6))
    for data, label in zip(cold_output, ['CERG', 'WARP', 'Storage Output']):
        plt.plot(range(8760), data, label=label)
    for data, label in zip(cold_input, ['Storage Input', 'Load']):
        plt.plot(range(8760), [-x for x in data], label=label)
    plt.title(f'{city_name} - Cold')
    plt.legend(loc='upper right')
    plt.savefig(f'plots/stack_plots/{city_name}_cold.png')
    plt.close()

if __name__ == '__main__':
    city_map = {1: "Beijing", 2: "Guangzhou", 3: "Wuhan", 4: "Wulumuqi"}
    for city_code in city_map:
        m = optimal_plan(city_code,0,3.8)
        plot_stacked_area(m, city_map[city_code])