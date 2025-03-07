import os
import pandas as pd

def convert_csv_to_excel(folder_path, data_folder_path):
    combined_df = pd.DataFrame()

    for filename in os.listdir(data_folder_path):
        if filename.endswith('_normalized.csv'):
            csv_file = os.path.join(data_folder_path, filename)
            city_name = filename.split('_')[1]  # 假设文件名格式为 "City_Device_Capacities.csv"

            # 读取 CSV 文件
            df = pd.read_csv(csv_file)
            if 'elec_load(MW)' in df.columns and 'heating_load(MW)' in df.columns and 'cooling_load(MW)' in df.columns:
                elec_load_avg = df[df['elec_load(MW)'] > 0]['elec_load(MW)'].mean()
                heat_load_avg = df[df['heating_load(MW)'] > 0]['heating_load(MW)'].mean()
                cold_load_avg = df[df['cooling_load(MW)'] > 0]['cooling_load(MW)'].mean()

                combined_df.loc['elec_load_avg (MW)', city_name] = elec_load_avg
                combined_df.loc['heat_load_avg (MW)', city_name] = heat_load_avg
                combined_df.loc['cold_load_avg (MW)', city_name] = cold_load_avg
            else:
                print(f"Columns not found in {csv_file}")

    # 按照指定顺序重新排序索引
    device_order = [
        'elec_load_avg (MW)', 'heat_load_avg (MW)', 'cold_load_avg (MW)', 'PV (m^2)', 'PV_Annual_Avg_Power (MW)', 'solar_thermal_collector (km^2)',
        'solar_thermal_collector_Annual_Avg_Power (MW)', 'CERG (MW)', 'CHP (MW)', 'Gas_Boiler (MW)', 'Heat_Pump (MW)', 'Electric_Boiler (MW)', 'WARP (MW)',
        'Heat_Storage (MW)', 'Cold_Storage (MW)', 'Elec_Storage (MW)', 'Seasonal_Heat_Storage (MW)'
    ]
    combined_df = combined_df.rename(index={'SC': 'solar_thermal_collector'})
    combined_df = combined_df.reindex(device_order)

    # 检查 combined_df 是否为空
    if combined_df.empty:
        print("No data to save.")
    else:
        # 将总表格保存为 Excel 文件
        excel_file = os.path.join(folder_path, 'combined_device_capacities.xlsx')
        combined_df.to_excel(excel_file)
        print(f'Combined data saved to {excel_file}')

if __name__ == '__main__':
    folder_path = '/Users/liuboyuan/Desktop/ploting/device_capacities'
    data_folder_path = '/Users/liuboyuan/Desktop/ploting/data/noramlized'
    convert_csv_to_excel(folder_path, data_folder_path)