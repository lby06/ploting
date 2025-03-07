import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import csv
import pandas as pd
from optimal_plan import optimal_plan
from optimal_plan import old_equal
carbon_price = 0
pv_space = 3.8

 
    # m.conversion_device_list = [heat_elec_collab, elec_boiler,compress_cold,\
    #                         absorb_cold, gas_boilder, Ground_source_heat_pump_heat,\
    #                         Ground_source_heat_pump_cold]





def generate_flow_data(model, output_file, city_code):
    data = []

    # Conversion devices and cost
    heat_elec_collab = model.conversion_device_list[0]
    heat_elec_collab_invest_cost = heat_elec_collab.cost * model.convert_invest[0].value
    elec_boiler = model.conversion_device_list[1]
    elec_boiler_invest_cost = elec_boiler.cost * model.convert_invest[1].value
    compress_cold = model.conversion_device_list[2]
    compress_cold_invest_cost = compress_cold.cost * model.convert_invest[2].value
    absorb_cold = model.conversion_device_list[3]
    absorb_cold_invest_cost = absorb_cold.cost * model.convert_invest[3].value
    gas_boiler = model.conversion_device_list[4]
    gas_boiler_invest_cost = gas_boiler.cost * model.convert_invest[4].value
    ground_heat_pump_heat = model.conversion_device_list[5]
    ground_heat_pump_heat_invest_cost = ground_heat_pump_heat.cost * model.convert_invest[5].value
    ground_heat_pump_cold = model.conversion_device_list[6]
    ground_heat_pump_cold_invest_cost = ground_heat_pump_cold.cost * model.convert_invest[6].value



    # 购电：电价
    for energy_kind in model.set_buy_energy:
        if energy_kind != "gas":
            # 成本/发电量
            total_elec_input = sum(model.buy_energy[energy_kind, t]() for t in model.t_8760)
            elec_purchase = sum(model.elec_price[t]* model.buy_energy[energy_kind, t]()for t in model.t_8760) / 10000 / total_elec_input
            data.append([energy_kind + "input", energy_kind, total_elec_input, elec_purchase])

    # PV ：成本/发电量
    pv = model.solar_device_list[0]
    pv_output = sum(model.solar_energy[pv.output_kind[0], t]() for t in model.t_8760)
    pv_cost = (old_equal(1020.005, 25) * (model.solar_Area[0]() * pv.area_rate))/ pv_output
    data.append(["PV", pv.output_kind[0], pv_output, pv_cost])

    #导入各个转换设备的容量来获取成本
    # 记录储能设备的投资成本
    elec_storage_invest_cost = 0
    cold_storage_invest_cost = 0
    heat_storage_invest_cost = 0
    seasonal_heat_storage_invest_cost = 0

    for device_id in range(len(model.storage_device_list)):
        the_device = model.storage_device_list[device_id]
        if the_device.label == "elec_storage":
            elec_storage_invest_cost = the_device.cost * model.storage_invest[device_id]
        elif the_device.label == "cold_storage":
            cold_storage_invest_cost = the_device.cost * model.storage_invest[device_id]
        elif the_device.label == "heat_storage":
            heat_storage_invest_cost = the_device.cost * model.storage_invest[device_id]
        elif the_device.label == "seasonal_heat_storage":
            seasonal_heat_storage_invest_cost = the_device.cost * model.storage_invest[device_id]


    # Gas Boiler
    # 购气：气价
    input_key = gas_boiler.label + "_" + gas_boiler.input_kind
    gas_boiler_input = sum(model.convert_power[input_key, t]() for t in model.t_8760)
    gas_boiler_input_cost = sum(model.gas_price[t] * model.convert_power[input_key, t]() for t in model.t_8760) / 10000 / gas_boiler_input

    data.append([gas_boiler.input_kind, gas_boiler.label, gas_boiler_input, gas_boiler_input_cost])
    # 转化后热:总气价加上Gas Boiler成本/发热量
    for output_kind in gas_boiler.output_kind:
        output_key = gas_boiler.label + "_" + output_kind
        gas_boiler_output = sum(model.convert_power[output_key, t]() for t in model.t_8760)
        gas_boiler_output_cost = (gas_boiler_input_cost * gas_boiler_input+ gas_boiler_invest_cost) / gas_boiler_output
        data.append([gas_boiler.label, output_kind, gas_boiler_output, gas_boiler_output_cost])

    # Heat-Elec Collaboration (CHP)
    input_key = heat_elec_collab.label + "_" + heat_elec_collab.input_kind
    heat_elec_collab_input = sum(model.convert_power[input_key, t]() for t in model.t_8760)
    data.append([heat_elec_collab.input_kind, heat_elec_collab.label, heat_elec_collab_input, gas_boiler_input_cost])
    for output_kind in heat_elec_collab.output_kind:
        output_key = heat_elec_collab.label + "_" + output_kind
        heat_elec_collab_output = sum(model.convert_power[output_key, t]() for t in model.t_8760)
        if heat_elec_collab_output != 0:
            heat_elec_collab_output_cost = (gas_boiler_input_cost * heat_elec_collab_input + heat_elec_collab_invest_cost) / heat_elec_collab_output
            data.append([heat_elec_collab.label, output_kind, heat_elec_collab_output, heat_elec_collab_output_cost])
        else:
            heat_elec_collab_output_cost = 0
    elec_CHP_output = sum(model.convert_power["CHP_elec", t]() for t in model.t_8760)
    heat_CHP_output = sum(model.convert_power["CHP_heat", t]() for t in model.t_8760)
    if elec_CHP_output != 0:
        elec_CHP_output_cost = (gas_boiler_output_cost * heat_elec_collab_input + heat_elec_collab_invest_cost) / elec_CHP_output
    else:
        elec_CHP_output_cost = 0
    if heat_CHP_output != 0:
        heat_CHP_output_cost = (gas_boiler_output_cost * heat_elec_collab_input + heat_elec_collab_invest_cost) / heat_CHP_output
    else:
        heat_CHP_output_cost = 0


    # elec_bus的电价
    elec_bus_output = (elec_purchase * total_elec_input +
                       pv_cost * pv_output +
                          elec_CHP_output_cost * elec_CHP_output +
                       elec_storage_invest_cost) / (total_elec_input + pv_output + elec_CHP_output)

    # Electric Boiler
    input_key = elec_boiler.label + "_" + elec_boiler.input_kind
    elec_boiler_input = sum(model.convert_power[input_key, t]() for t in model.t_8760)
    data.append([elec_boiler.input_kind, elec_boiler.label, elec_boiler_input, elec_bus_output])
    for output_kind in elec_boiler.output_kind:
        output_key = elec_boiler.label + "_" + output_kind
        elec_boiler_output = sum(model.convert_power[output_key, t]() for t in model.t_8760)
        # output为0时，成本为0
        if elec_boiler_output != 0:
            elec_boiler_output_cost = (elec_bus_output * elec_boiler_input + elec_boiler_invest_cost) / elec_boiler_output
        else:
            elec_boiler_output_cost = 0
        data.append([elec_boiler.label, output_kind, elec_boiler_output, elec_boiler_output_cost])

    # Compress Cold (CERG)
    input_key = compress_cold.label + "_" + compress_cold.input_kind
    compress_cold_input = sum(model.convert_power[input_key, t]() for t in model.t_8760)
    data.append([compress_cold.input_kind, compress_cold.label, compress_cold_input, elec_bus_output])
    for output_kind in compress_cold.output_kind:
        output_key = compress_cold.label + "_" + output_kind
        compress_cold_output = sum(model.convert_power[output_key, t]() for t in model.t_8760)
        compress_cold_output_cost = (elec_bus_output * compress_cold_input + compress_cold_invest_cost) / compress_cold_output
        data.append([compress_cold.label, output_kind, compress_cold_output, compress_cold_output_cost])

    # Ground Source Heat Pump Heat
    input_key = ground_heat_pump_heat.label + "_" + ground_heat_pump_heat.input_kind
    ground_heat_pump_heat_input = sum(model.convert_power[input_key, t]() for t in model.t_8760)
    data.append([ground_heat_pump_heat.input_kind, ground_heat_pump_heat.label, ground_heat_pump_heat_input, elec_bus_output])
    for output_kind in ground_heat_pump_heat.output_kind:
        output_key = ground_heat_pump_heat.label + "_" + output_kind
        ground_heat_pump_heat_output = sum(model.convert_power[output_key, t]() for t in model.t_8760)
        if ground_heat_pump_heat_output != 0:
            ground_heat_pump_heat_output_cost = (elec_bus_output * ground_heat_pump_heat_input + ground_heat_pump_heat_invest_cost) / ground_heat_pump_heat_output
        else:
            ground_heat_pump_heat_output_cost = 0
        data.append([ground_heat_pump_heat.label, output_kind, ground_heat_pump_heat_output, ground_heat_pump_heat_output_cost])

    # Ground Source Heat Pump Cold
    input_key = ground_heat_pump_cold.label + "_" + ground_heat_pump_cold.input_kind
    ground_heat_pump_cold_input = sum(model.convert_power[input_key, t]() for t in model.t_8760)
    data.append([ground_heat_pump_cold.input_kind, ground_heat_pump_cold.label, ground_heat_pump_cold_input, elec_bus_output])
    for output_kind in ground_heat_pump_cold.output_kind:
        output_key = ground_heat_pump_cold.label + "_" + output_kind
        ground_heat_pump_cold_output = sum(model.convert_power[output_key, t]() for t in model.t_8760)
        if ground_heat_pump_cold_output != 0:
            ground_heat_pump_cold_output_cost = (elec_bus_output * ground_heat_pump_cold_input + ground_heat_pump_cold_invest_cost) / ground_heat_pump_cold_output
        else:
            ground_heat_pump_cold_output_cost = 0
        data.append([ground_heat_pump_cold.label, output_kind, ground_heat_pump_cold_output, ground_heat_pump_cold_output_cost])

    # Heat Bus and Cold Bus的价格
    heat_bus_output = (gas_boiler_output_cost * gas_boiler_output + 
                       heat_elec_collab_output_cost * heat_elec_collab_output + 
                       ground_heat_pump_heat_output_cost * ground_heat_pump_heat_output + 
                       heat_CHP_output_cost * heat_CHP_output +
                       heat_storage_invest_cost +
                       seasonal_heat_storage_invest_cost) / (gas_boiler_output + heat_elec_collab_output + ground_heat_pump_heat_output + heat_CHP_output)
    cold_bus_output = (compress_cold_output_cost * compress_cold_output +
                       ground_heat_pump_cold_output_cost * ground_heat_pump_cold_output +
                          cold_storage_invest_cost) / (compress_cold_output + ground_heat_pump_cold_output)

    # Storage devices
   

    # Elec Storage
    elec_storage_index = next(i for i, device in enumerate(model.storage_device_list) if device.label == "Elec_Storage")
    elec_storage = model.storage_device_list[elec_storage_index]
    elec_storage_charge = sum(model.storage_charge_power[elec_storage_index, t]() for t in model.t_8760)
    elec_storage_discharge = sum(model.storage_discharge_power[elec_storage_index, t]() for t in model.t_8760)
    data.append([elec_storage.input_kind, elec_storage.label, elec_storage_charge, elec_bus_output])
    data.append([elec_storage.label, elec_storage.output_kind, elec_storage_discharge, elec_bus_output])

    # Heat Storage
    heat_storage_index = next(i for i, device in enumerate(model.storage_device_list) if device.label == "Heat_Storage")
    heat_storage = model.storage_device_list[heat_storage_index]
    heat_storage_charge = sum(model.storage_charge_power[heat_storage_index, t]() for t in model.t_8760)
    heat_storage_discharge = sum(model.storage_discharge_power[heat_storage_index, t]() for t in model.t_8760)
    data.append([heat_storage.input_kind, heat_storage.label, heat_storage_charge, heat_bus_output])
    data.append([heat_storage.label, heat_storage.output_kind, heat_storage_discharge, heat_bus_output])

    # Cold Storage
    cold_storage_index = next(i for i, device in enumerate(model.storage_device_list) if device.label == "Cold_Storage")
    cold_storage = model.storage_device_list[cold_storage_index]
    cold_storage_charge = sum(model.storage_charge_power[cold_storage_index, t]() for t in model.t_8760)
    cold_storage_discharge = sum(model.storage_discharge_power[cold_storage_index, t]() for t in model.t_8760)
    data.append([cold_storage.input_kind, cold_storage.label, cold_storage_charge, cold_bus_output])
    data.append([cold_storage.label, cold_storage.output_kind, cold_storage_discharge, cold_bus_output])

    # Seasonal Heat Storage
    seasonal_heat_storage_index = next(i for i, device in enumerate(model.storage_device_list) if device.label == "Seasonal_Heat_Storage")
    seasonal_heat_storage = model.storage_device_list[seasonal_heat_storage_index]
    seasonal_heat_storage_charge = sum(model.storage_charge_power[seasonal_heat_storage_index, t]() for t in model.t_8760)
    seasonal_heat_storage_discharge = sum(model.storage_discharge_power[seasonal_heat_storage_index, t]() for t in model.t_8760)
    print(seasonal_heat_storage_charge)
    print(seasonal_heat_storage_discharge)
    data.append([seasonal_heat_storage.input_kind, seasonal_heat_storage.label, seasonal_heat_storage_charge, heat_bus_output])
    data.append([seasonal_heat_storage.label, seasonal_heat_storage.output_kind, seasonal_heat_storage_discharge, heat_bus_output])

    # # Solar devices
    # pv = model.solar_device_list[0]
    # sc = model.solar_device_list[1]

    # # PV
    # pv_output = sum(model.solar_energy[pv.output_kind[0], t]() for t in model.t_8760) / 8760
    # data.append(["PV", pv.output_kind[0], pv_output])

    # # Solar Thermal Collector
    # sc_output = sum(model.solar_energy[sc.output_kind[0], t]() for t in model.t_8760)
    # data.append(["SC", sc.output_kind[0], sc_output])
    # Load
    #load 
    city_map = {
        1: "Beijing",
        2: "Guangzhou",
        3: "Wuhan",
        4: "Wulumuqi"
    }
    
    if city_code not in city_map:
        raise ValueError("Invalid city code. Please enter a number between 1 and 4.")
    
    file_name = f"/Users/liuboyuan/Desktop/ploting/data/noramlized/{city_code}_{city_map[city_code]}_data_normalized.csv"
    
    # 读取数据
    df = pd.read_csv(file_name)
    elec_load = df['elec_load(MW)'].tolist()
    heat_load = df['heating_load(MW)'].tolist()
    cold_load = df['cooling_load(MW)'].tolist()
    data.append(["elec", "elec_load", sum(elec_load) ,elec_bus_output])
    data.append(["heat", "heat_load", sum(heat_load) ,heat_bus_output])
    data.append(["cold", "cold_load", sum(cold_load) ,cold_bus_output])

    # Write to CSV
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["source", "target", "weight", "cost"])
        writer.writerows(data)
    
    print(f"City Name: {city_map[city_code]}")
    print(f"Elec Bus Cost: {elec_bus_output}")
    print(f"Heat Bus Cost: {heat_bus_output}")
    print(f"Cold Bus Cost: {cold_bus_output}")

if __name__ == '__main__':

    city_map = {
        1: "Beijing",
        2: "Guangzhou",
        3: "Wuhan",
        4: "Wulumuqi"
    }
    for city_code in city_map.keys():
        city_name = city_map[city_code]
    
        m = optimal_plan(city_code,carbon_price,pv_space)
        output_file = f'/Users/liuboyuan/Desktop/ploting/plots/cost_plots/{city_name}_generated_flow_data.csv'
        generate_flow_data(m, output_file, city_code)