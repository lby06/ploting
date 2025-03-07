import pandas as pd
 # 燃气碳排放系数，单位吨/MWh
# 处理手法1：对负荷进行缩放处理
def load_scaling(load, scale):
    load_scaled = [i * (1 + scale / 100) for i in load]
    return load_scaled

def read_data(city_code, load, scale):
    gas_carbon = 0.2165
    # 根据输入的城市代码选择对应的文件名
    city_map = {
        1: "Beijing",
        2: "Guangzhou",
        3: "Wuhan",
        4: "Wulumuqi"
    }
    
    if city_code not in city_map:
        raise ValueError("Invalid city code. Please enter a number between 1 and 4.")
    
    file_name = f"/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_map[city_code]}_data_normalized.csv"
    file_name2 = f"/Users/liuboyuan/Desktop/ploting/normalized_carbon_factors.csv"

    # 读取数据
    df = pd.read_csv(file_name)
    elec_load = df['elec_load(MW)'].tolist()
    heat_load = df['heating_load(MW)'].tolist()
    cold_load = df['cooling_load(MW)'].tolist()
    elec_price = df['elec_price(HKD/MWh)'].tolist()
    gas_price = df['gas_price(HKD/m^3)'].tolist()
    pv_I = df['PV'].tolist()  # 归一化的光伏UNits
    # 读取碳排放系数
    carbon_df = pd.read_csv(file_name2)
    if city_code == 1:
        elec_carbon = carbon_df['1'].tolist()
    elif city_code == 2:
        elec_carbon = carbon_df['2'].tolist()
    elif city_code == 3:
        elec_carbon = carbon_df['3'].tolist()
    elif city_code == 4:
        elec_carbon = carbon_df['4'].tolist()
    
    # 统一燃气的单位从立方米变为MWh
    for i in range(8760):
        gas_price[i] = gas_price[i] * 100

    
    # 根据输入的load和scale选择对应的处理方式
    if load == 'elec':
        elec_load = load_scaling(elec_load, scale)
    elif load == 'heat':
        heat_load = load_scaling(heat_load, scale)
    elif load == 'cold':
        cold_load = load_scaling(cold_load, scale)
    elif load == 'pv':
        pv_I = load_scaling(pv_I, scale)
    elif load == 'carbon_factor':
        elec_carbon = load_scaling(elec_carbon, scale)
        gas_carbon = gas_carbon * (1 + scale / 100)
    else:
        # 不进行处理
        pass
    
    return elec_load, heat_load, cold_load, elec_price, gas_price, pv_I, elec_carbon, gas_carbon