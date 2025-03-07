import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# 添加搜索路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from optimal_plan import optimal_plan


def save_device_capacities(m, city_name):
    # 创建保存结果的文件夹
    output_folder = os.path.join(os.getcwd(), 'device_capacities')
    os.makedirs(output_folder, exist_ok=True)

    # 收集设备容量数据
    device_data = []
    for device in m.set_converter:
        device_data.append({
            'City': city_name,
            'Device': m.conversion_device_list[device].label + ' (MW)',
            'Capacity': m.convert_invest[device]()
        })
    for device in m.set_storage:
        t_duration = m.storage_device_list[device].t_duration
        device_label = m.storage_device_list[device].label
        if device_label == "Seasonal_Heat_Storage":
            device_label += " (MWh)"
        else:
            device_label += " (MW)"
        device_data.append({
            'City': city_name,
            'Device': device_label,
            'Capacity': m.storage_invest[device]() / t_duration
        })
    device_data.append({
        'City': city_name,
        'Device': 'PV (km^2)',
        'Capacity': m.solar_Area[0]()
    })
    device_data.append({
        'City': city_name,
        'Device': 'solar_thermal_collector (km^2)',
        'Capacity': m.solar_Area[1]()
    })

    # 计算 PV 年最大平均功率
    pv_area = m.solar_Area[0]()
    pv_efficiency = m.solar_device_list[0].efficiency[0]
    pv_input = m.pv_I
    pv_area_rate = m.solar_device_list[0].area_rate
    pv_maxium_annual_power = sum(pv_area * pv_efficiency * pv_input[t] * pv_area_rate for t in m.t_8760) / len(m.t_8760)
    device_data.append({
        'City': city_name,
        'Device': 'PV_Annual_maxium_Avg_Power (MW)',
        'Capacity': pv_maxium_annual_power
    })
        # 计算 PV 年实际负荷平均功率
    pv_area = m.solar_Area[0]()
    pv_efficiency = m.solar_device_list[0].efficiency[0]
    pv_input = m.pv_I
    pv_area_rate = m.solar_device_list[0].area_rate
    pv_annual_power = sum(m.solar_energy["elec", t]() for t in m.t_8760) / len(m.t_8760)
    device_data.append({
        'City': city_name,
        'Device': 'PV_Annual_Avg_Power (MW)',
        'Capacity': pv_annual_power
    })

    # 计算 solar_thermal_collector 年平均功率
    sc_area = m.solar_Area[1]()
    sc_efficiency = m.solar_device_list[1].efficiency[0]
    sc_input = m.pv_I
    sc_area_rate = m.solar_device_list[1].area_rate
    sc_annual_power = sum(sc_area * sc_efficiency * sc_input[t] * sc_area_rate for t in m.t_8760) / len(m.t_8760)
    device_data.append({
        'City': city_name,
        'Device': 'solar_thermal_collector_Annual_Avg_Power (MW)',
        'Capacity': sc_annual_power
    })

    # 保存设备容量数据到 CSV 文件
    df = pd.DataFrame(device_data)
    csv_file = os.path.join(output_folder, f'{city_name}_device_capacities.csv')
    df.to_csv(csv_file, index=False)

    return df

def combine_device_capacities(city_map, data_folder_path):
    combined_df = pd.DataFrame()

    for city_code, city_name in city_map.items():
        m = optimal_plan(city_code,0,3.8)
        df = save_device_capacities(m, city_name)
        df.set_index('Device', inplace=True)
        df = df[['Capacity']]
        df.columns = [city_name]

        if combined_df.empty:
            combined_df = df
        else:
            combined_df = combined_df.join(df, how='outer')

        # 读取各类负荷功率平均值并加入到总表格中
        normalized_file = os.path.join(data_folder_path, f'{city_code}_{city_name}_data_normalized.csv')
        if os.path.exists(normalized_file):
            df_load = pd.read_csv(normalized_file)
            if 'elec_load(MW)' in df_load.columns and 'heating_load(MW)' in df_load.columns and 'cooling_load(MW)' in df_load.columns:
                elec_load_avg = df_load[df_load['elec_load(MW)'] > 0]['elec_load(MW)'].mean()
                heat_load_avg = df_load[df_load['heating_load(MW)'] > 0]['heating_load(MW)'].mean()
                cold_load_avg = df_load[df_load['cooling_load(MW)'] > 0]['cooling_load(MW)'].mean()

                combined_df.loc['elec_load_avg (MW)', city_name] = elec_load_avg
                combined_df.loc['heat_load_avg (MW)', city_name] = heat_load_avg
                combined_df.loc['cold_load_avg (MW)', city_name] = cold_load_avg
            else:
                print(f"Columns not found in {normalized_file}")

    # 按照指定顺序重新排序索引
    device_order = [
        'elec_load_avg (MW)', 'heat_load_avg (MW)', 'cold_load_avg (MW)', 'PV (km^2)', 'PV_Annual_maxium_Avg_Power (MW)','PV_Annual_Avg_Power (MW)', 'solar_thermal_collector (km^2)',
        'solar_thermal_collector_Annual_Avg_Power (MW)', 'CERG (MW)', 'CHP (MW)', 'Gas_Boiler (MW)', 'Ground_Heat_Pump_heat (MW)','Electric_Boiler (MW)', 'WARP (MW)',
        'Heat_Storage (MW)', 'Cold_Storage (MW)', 'Elec_Storage (MW)', 'Seasonal_Heat_Storage (MWh)', 'Seasonal_heat_storage_charge (MW)', 'Seasonal_heat_storage_discharge (MW)'
    ]
    combined_df = combined_df.reindex(device_order)

    # 将总表格保存为 Excel 文件
    output_folder = os.path.join(os.getcwd(), 'device_capacities')
    excel_file = os.path.join(output_folder, 'combined_device_capacities.xlsx')
    combined_df.to_excel(excel_file)
    print(f'Combined data saved to {excel_file}')

    # 绘制设备容量图表
    combined_df.plot(kind='bar', figsize=(12, 8))
    plt.xlabel('Device')
    plt.ylabel('Capacity')
    plt.title('Device Capacities Across Cities')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'combined_device_capacities.png'))
    plt.close()

if __name__ == '__main__':
    city_map = {1: "Beijing", 2: "Guangzhou", 3: "Wuhan", 4: "Wulumuqi"}
    data_folder_path = '/Users/liuboyuan/Desktop/ploting/data/noramlized'
    combine_device_capacities(city_map, data_folder_path)