import pandas as pd

df = pd.read_excel('/Users/liuboyuan/Desktop/ploting/device_capacities/combined_device_capacities.xlsx')

# 打印行名以确认行名是否正确
print(df.index)

# 在最下面增加新的一行seasonal_heat_storage_charge = Ground_Heat_Pump_cold(MW) * 7
df.loc['seasonal_heat_storage_charge'] = df.loc['Ground_Heat_Pump_heat (MW)'] * 7

# 增加一行seasonal_heat_storage_discharge = Ground_Heat_Pump_heat(MW) * 3
df.loc['seasonal_heat_storage_discharge'] = df.loc['Ground_Heat_Pump_heat (MW)'] * 3

# 保存到combined_device_capacities.xlsx
df.to_excel('/Users/liuboyuan/Desktop/ploting/device_capacities/combined_device_capacities.xlsx', index=False)