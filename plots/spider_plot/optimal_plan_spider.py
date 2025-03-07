from pyomo.environ import *
import pandas as pd
import time
from data_process import read_data
big_M = 1e6



#-----------------------------------------------------
# 设备类定义
#光伏发电/太阳能集热器
class solar_device:
    def __init__(self, label, efficiency, output_kind, cost, area_rate):
        self.label = label              # 记录设备名称
        self.efficiency = efficiency    # 列表，表示可能的能源类型的输出的效率
        self.output_kind = output_kind  # 列表，表示输出的各个能源类型
        self.cost = cost                # 表示单位输入容量设备的建设成本
        self.area_rate = area_rate # 表示单位面积的发电/集热量 单位为MW/m^2
        pass

# 能量转化设备
class conversion_device:
    # 能量转换设备
    def __init__(self, label, efficiency, input_kind, output_kind, cost):
        # 首先记录设备的基本信息
        self.label = label              # 记录设备名称
        self.efficiency = efficiency    # 列表，表示可能的多种能源类型的输出
        self.input_kind = input_kind    # 字符串，表示输入能源类型种类（暂时只支持单类型能源输入）
        self.output_kind = output_kind  # 列表，表示输出的各个能源类型
        self.cost = cost                # 表示单位输入容量设备的建设成本
        pass

class storage_device:
    # 能量储存设备
    def __init__(self, label, input_efficiency, output_efficiency, input_kind,\
        output_kind, cost, self_discharge_rate, t_duration):
        self.label = label              # 记录设备名称
        self.input_efficiency = input_efficiency    # 数值
        self.output_efficiency = output_efficiency  # 数值
        self.input_kind = input_kind                # 单个字符串，表示输入能源类型种类
        self.output_kind = output_kind              # 单个字符串，表示的各个能源类型
        self.cost = cost                            # 表示单位储能容量设备的建设成本
        self.self_discharge_rate = self_discharge_rate  # 自放电率
        self.t_duration = t_duration                # 表示储能设备的循环
        pass

# 读取输入数据


# 折旧率计算函数
def old_equal(cost, year):
    return 0.06/(1-(1+0.06)**(-year))*cost

def optimal_plan(city_code, carbon_price, pv_space, load, scale):

    # 记录开始的时间
    start_time = time.time()
    #print('Modeling...')
    #-----------------------------------------------------
    # 定义求解模型
    m = ConcreteModel()
    #-----------------------------------------------------
    # 首先将各个数据读入，并列表化。运行价格单位为元/MWh，在目标函数那边修正为万元/MWh
    elec_load, heat_load, cold_load, elec_price, gas_price, pv_I, elec_carbon, gas_carbon = read_data(city_code, load, scale)
    m.elec_load = elec_load
    m.heat_load = heat_load
    m.cold_load = cold_load
    m.elec_price = elec_price
    m.gas_price = gas_price
    m.elec_carbon = elec_carbon
    # 光伏发电/太阳能集热器的归一化后的比例
    m.pv_I = pv_I
    # 碳排放价格
    m.carbon_price = carbon_price
    m.pv_space = pv_space
    # 所有待规划设备的字典
    # 光伏发电/太阳能集热器
    pv = solar_device(label = "PV", efficiency=[0.83], output_kind = ["elec"], cost = old_equal(1020, 25), area_rate = 100)
    sc = solar_device(label = "SC", efficiency=[0.75], output_kind = ["heat"], cost = old_equal(604, 20), area_rate = 500)
    m.solar_device_list = [pv, sc]
    # 各能量转换设备信息录入
    heat_elec_collab = conversion_device(label = "CHP", efficiency=[0.22, 0.7], \
                                        input_kind = "gas", output_kind = ["elec", "heat"], cost = old_equal(800, 30))

    elec_boiler = conversion_device(label = "Electric_Boiler", efficiency=[0.9], \
                                        input_kind = "elec", output_kind = ["heat"], cost = old_equal(62, 20))
    compress_cold = conversion_device(label = "CERG", efficiency=[5], \
                                        input_kind = "elec", output_kind = ["cold"], cost = old_equal(60, 20))
    absorb_cold = conversion_device(label = "WARP", efficiency=[0.8], \
                                        input_kind = "heat", output_kind = ["cold"], cost = old_equal(60, 20))
    
    gas_boilder = conversion_device(label = "Gas_Boiler", efficiency=[0.95], \
                                        input_kind = "gas", output_kind = ["heat"], cost = old_equal(41.525, 20))
    
    #gas_source_heat_pump_heat = conversion_device(label = "Gas_Heat_Pump_heat", efficiency=[2.5], \
    #                                    input_kind = "elec", output_kind = ["heat"], cost = old_equal(431.86, 20))
    #gas_source_heat_pump_cold = conversion_device(label = "Gas_Heat_Pump_cold", efficiency=[6], \
    #                                    input_kind = "elec", output_kind = ["cold"], cost = 0)
    Ground_source_heat_pump_heat = conversion_device(label = "Ground_Heat_Pump_heat", efficiency=[4], \
                                        input_kind = "elec", output_kind = ["heat"], cost = old_equal(239.184, 20))
    Ground_source_heat_pump_cold = conversion_device(label = "Ground_Heat_Pump_cold", efficiency=[8], \
                                        input_kind = "elec", output_kind = ["cold"], cost = 0)
    
    m.conversion_device_list = [heat_elec_collab, elec_boiler,compress_cold,\
                            absorb_cold, gas_boilder, Ground_source_heat_pump_heat,\
                            Ground_source_heat_pump_cold]
    
    
    # 各储能设备信息录入
    elec_storage = storage_device(label = "Elec_Storage", input_efficiency = 0.9487, output_efficiency = 0.9487, \
                                input_kind = "elec", output_kind = "elec", cost = old_equal(453, 10), self_discharge_rate = 0.0005, t_duration = 2)
    heat_storage = storage_device(label = "Heat_Storage", input_efficiency = 0.894, output_efficiency = 0.894, \
                                input_kind = "heat", output_kind = "heat", cost = old_equal(11.325, 25), self_discharge_rate = 0.0075,  t_duration = 5)
    cold_storage = storage_device(label = "Cold_Storage", input_efficiency = 0.894, output_efficiency = 0.894, \
                                input_kind = "cold", output_kind = "cold", cost = old_equal(11.325, 25), self_discharge_rate = 0.0075,  t_duration = 5)
    Seasonal_Heat_Storage = storage_device(label = "Seasonal_Heat_Storage", input_efficiency = 0.866, output_efficiency = 0.866, \
                                input_kind = "heat", output_kind = "heat", cost = old_equal(1.1325, 30), self_discharge_rate = 0.00001,  t_duration = 1)
    m.storage_device_list = [elec_storage, heat_storage, cold_storage, Seasonal_Heat_Storage]
    
    #-------------------------------------------------------------------
    # 定义时刻
    m.t_8760 = Set(initialize = [_ for _ in range(8760)])
    m.day_365 = Set(initialize = [_ for _ in range(364)])
    #----------------------------------------
    # 定义0-1变量，用于判断是否使用季节性热储能
    m.seasonal_heat_storage_used = Var(within=Binary)
    # m.gas_source_heat_pump_heat_flag = Var(m.t_8760, within=Binary)
    # m.gas_source_heat_pump_cold_flag = Var(m.t_8760, within=Binary)
    # m.Ground_source_heat_pump_heat_flag = Var(m.t_8760, within=Binary)
    # m.Ground_source_heat_pump_cold_flag = Var(m.t_8760, within=Binary)
    # 初始化热泵使用标志为一8760长的列表
    m.gas_source_heat_pump_heat_flag = [0 for _ in range(8760)]
    m.gas_source_heat_pump_cold_flag = [0 for _ in range(8760)]
    m.Ground_source_heat_pump_heat_flag = [0 for _ in range(8760)]
    m.Ground_source_heat_pump_cold_flag = [0 for _ in range(8760)]

    if city_code == 1:
       cold_season_start = 2190
       cold_season_end = 6742
    elif city_code == 2:
       cold_season_start = 1460
       cold_season_end = 8030
    elif city_code == 3:
       cold_season_start = 4825
       cold_season_end = 7500
    elif city_code == 4:
       cold_season_start = 2920
       cold_season_end = 6400
    for t in m.t_8760:
       if t >= cold_season_start and t <= cold_season_end:
           m.gas_source_heat_pump_cold_flag[t] = 1
           m.gas_source_heat_pump_heat_flag[t] = 0
           m.Ground_source_heat_pump_cold_flag[t] = 1
           m.Ground_source_heat_pump_heat_flag[t] = 0
       else:
           m.gas_source_heat_pump_cold_flag[t] = 0
           m.gas_source_heat_pump_heat_flag[t] = 1
           m.Ground_source_heat_pump_cold_flag[t] = 0
           m.Ground_source_heat_pump_heat_flag[t] = 1


    # 定义转换设备下标列表
    converter_power_index = []
    for device in m.conversion_device_list:
        # 输入能源种类
        device_kind_name = device.label + "_" + device.input_kind
        converter_power_index.append(device_kind_name)
        # 输出能源种类
        for output_kind in device.output_kind:
            device_kind_name = device.label + "_" + output_kind
            converter_power_index.append(device_kind_name)
    
    m.set_converter_power = Set(initialize = converter_power_index)
    m.set_converter = Set(initialize = range(len(m.conversion_device_list)))
    m.set_storage = Set(initialize = range(len(m.storage_device_list)))

    #----------------------------------------
    # 转换设备相关变量约束定义
    # 转换设备功率变量
    m.convert_invest = Var(m.set_converter, within = NonNegativeReals)# 转换设备投资
    m.convert_power = Var(m.set_converter_power, m.t_8760, within = NonNegativeReals)

    # 转换设备约束定义
    # 首先定义转换效率相关的约束
    for device in m.conversion_device_list:
        for output in device.output_kind:
            # 检索output在设备输出列表中的位置
            i = device.output_kind.index(output)
            # 正式定义约束
            fun_name = "c_{}_{}".format(device.label, output)
            input_kind = device.label + "_" + device.input_kind
            output_kind = device.label + "_" + output
            code_str = f'def {fun_name}(model, t):\n\t' \
                    f'return {device.efficiency[i]} * model.convert_power["{input_kind}",  t] == model.convert_power["{output_kind}", t]'
            
            local_env = {'m': m}
            exec(code_str, globals(), local_env)
            exec(f"m.constraint_{fun_name} = Constraint( m.t_8760, rule={fun_name})", globals(), local_env)
    
    # 然后定义设备输入容量上限
    def c_max_converter_input(model, device_id, t):
        m = model
        the_device = m.conversion_device_list[device_id]
        input_key = the_device.label + "_" + the_device.input_kind
        
        return m.convert_power[input_key, t] <= m.convert_invest[device_id]
    m.c_max_converter_input = Constraint(m.set_converter, m.t_8760, rule=c_max_converter_input)
    # heat_pump的容量约束
    #def c_gas_source_heat_pump(model):
    #    m = model
    #    gas_heat_pump_heat_index = next(i for i, device in enumerate(m.conversion_device_list) if device.label == "Gas_Heat_Pump_heat")
    #    gas_heat_pump_cold_index = next(i for i, device in enumerate(m.conversion_device_list) if device.label == "Gas_Heat_Pump_cold")
    #    return m.convert_invest[gas_heat_pump_heat_index] == m.convert_invest[gas_heat_pump_cold_index]
    #m.c_gas_source_heat_pump = Constraint(rule=c_gas_source_heat_pump)

    def c_Ground_source_heat_pump(model):
        m = model
        Ground_heat_pump_heat_index = next(i for i, device in enumerate(m.conversion_device_list) if device.label == "Ground_Heat_Pump_heat")
        Ground_heat_pump_cold_index = next(i for i, device in enumerate(m.conversion_device_list) if device.label == "Ground_Heat_Pump_cold")
        return m.convert_invest[Ground_heat_pump_heat_index] == m.convert_invest[Ground_heat_pump_cold_index]
    m.c_Ground_source_heat_pump = Constraint(rule=c_Ground_source_heat_pump)
    #heat pump的0-1约束
    # def c_gas_source_heat_pump_flag(model, t):
    #     m = model
    #     return m.gas_source_heat_pump_heat_flag[t] + m.gas_source_heat_pump_cold_flag[t] <= 1
    # m.c_gas_source_heat_pump_flag = Constraint(m.t_8760, rule=c_gas_source_heat_pump_flag)
    # def c_Ground_source_heat_pump_flag(model, t):
    #     m = model
    #     return m.Ground_source_heat_pump_heat_flag[t] + m.Ground_source_heat_pump_cold_flag[t] <= 1
    # m.c_Ground_source_heat_pump_flag = Constraint(m.t_8760, rule=c_Ground_source_heat_pump_flag)

    #对输入的能量采取约束
    #def c_gas_source_heat_pump_heat_input(model, t):
    #    m = model
    #    return m.convert_power["Gas_Heat_Pump_heat_elec", t] <= m.gas_source_heat_pump_heat_flag[t] * big_M
    #m.c_gas_source_heat_pump_input = Constraint(m.t_8760, rule=c_gas_source_heat_pump_heat_input)
    
    def c_Ground_source_heat_pump_heat_input(model, t):
        m = model
        return m.convert_power["Ground_Heat_Pump_heat_elec", t] <= m.Ground_source_heat_pump_heat_flag[t] * big_M
    m.c_Ground_source_heat_pump_input = Constraint(m.t_8760, rule=c_Ground_source_heat_pump_heat_input)
    
    #def c_gas_source_heat_pump_cold_input(model, t):
    #    m = model
    #    return m.convert_power["Gas_Heat_Pump_cold_elec", t] <= m.gas_source_heat_pump_cold_flag[t] * big_M
    #m.c_gas_source_heat_pump_output = Constraint(m.t_8760, rule=c_gas_source_heat_pump_cold_input)
    
    def c_Ground_source_heat_pump_cold_input(model, t):
        m = model
        return m.convert_power["Ground_Heat_Pump_cold_elec", t] <= m.Ground_source_heat_pump_cold_flag[t] * big_M
    m.c_Ground_source_heat_pump_output = Constraint(m.t_8760, rule=c_Ground_source_heat_pump_cold_input)

#----------------------------------------
    m.storage_invest = Var(m.set_storage, within = NonNegativeReals)
    m.storage_charge_power = Var(m.set_storage,  m.t_8760, within = NonNegativeReals)
    m.storage_discharge_power = Var(m.set_storage,  m.t_8760, within = NonNegativeReals)
    m.storage_soc = Var(m.set_storage, m.t_8760, within = NonNegativeReals)

    # 季节性储能输入输出关联地源热泵
    # 季节性储热从热网和冷网额外接受的能量决策变量
    m.seasonal_heat_storage_heating = Var(m.t_8760, within = NonNegativeReals)
    m.seasonal_heat_storage_cooling = Var(m.t_8760, within = NonNegativeReals)
    
    # 输入与热泵制冷功率关联
    def c_seasonal_heat_storage_input(model, t):
        m = model
        seasonal_heat_storage_index = next(i for i, device in enumerate(m.storage_device_list) if device.label == "Seasonal_Heat_Storage")
        return m.storage_charge_power[seasonal_heat_storage_index, t] == (8 + 1) * m.convert_power["Ground_Heat_Pump_cold_elec", t] + m.seasonal_heat_storage_heating[t]
    m.c_seasonal_heat_storage_input = Constraint(m.t_8760, rule=c_seasonal_heat_storage_input)

    # 输出与热泵制热功率关联
    def c_seasonal_heat_storage_output(model, t):
        m = model
        seasonal_heat_storage_index = next(i for i, device in enumerate(m.storage_device_list) if device.label == "Seasonal_Heat_Storage")
        return m.storage_discharge_power[seasonal_heat_storage_index, t] == (4 - 1) * m.convert_power["Ground_Heat_Pump_heat_elec", t] + m.seasonal_heat_storage_cooling[t]
    m.c_seasonal_heat_storage_output = Constraint(m.t_8760, rule=c_seasonal_heat_storage_output)

    # 定义储存能量转移约束
    def c_storage_transfer(model, storage_id, t):
        m = model
        the_device = m.storage_device_list[storage_id]
        if t == 0:
            return m.storage_soc[storage_id, 0] == m.storage_soc[storage_id, 8759] * (1 - the_device.self_discharge_rate)  \
                + m.storage_charge_power[storage_id, 0] * the_device.input_efficiency \
                - m.storage_discharge_power[storage_id, 0] / the_device.output_efficiency
        else:
            return m.storage_soc[storage_id, t] == m.storage_soc[storage_id, t-1] * (1 - the_device.self_discharge_rate)  \
                + m.storage_charge_power[storage_id, t] * the_device.input_efficiency \
                - m.storage_discharge_power[storage_id, t] / the_device.output_efficiency
    m.c_storage_transfer = Constraint(m.set_storage, m.t_8760, rule = c_storage_transfer)
    
    # 定义储存设备日循环约束
    def c_short_term_storage_daily_cycle(model, storage_id, day):
        m = model
        the_device = m.storage_device_list[storage_id]
        # 对于季节性储能，不需要这个约束
        if the_device.label == "Seasonal_Heat_Storage":
            return Constraint.Skip
        start_time = day * 24
        end_time = (day + 1) * 24
        return m.storage_soc[storage_id, start_time] == m.storage_soc[storage_id, end_time]
    m.c_short_term_storage_daily_cycle = Constraint(m.set_storage, m.day_365, rule=c_short_term_storage_daily_cycle)
    
    # 然后定义设备输入容量上限
    def c_max_storage_input(model, storage_id, t):
        m = model
        the_device = m.storage_device_list[storage_id]
        # 季节性储能不需要这个约束
        if the_device.label != "Seasonal_Heat_Storage":
            return m.storage_charge_power[storage_id, t] <= m.storage_invest[storage_id] / the_device.t_duration
        else:
            return Constraint.Skip
    m.c_max_storage_input = Constraint(m.set_storage, m.t_8760, rule=c_max_storage_input) 
    
    # 定义设备充放功率互斥约束
    #def c_storage_charge_flag(model, storage_id, t):
    #    m = model
    #    return m.storage_charge_power[storage_id, t] <= big_M * m.storage_charge_flag[storage_id, t]
    #m.c_storage_charge_flag = Constraint(m.set_storage, m.t_8760, rule = c_storage_charge_flag)
    
    def c_max_storage_output(model, storage_id,  t):
        m = model
        the_device = m.storage_device_list[storage_id]
        # 季节性储能不需要这个约束
        if the_device.label != "Seasonal_Heat_Storage":
            return m.storage_discharge_power[storage_id, t] <= m.storage_invest[storage_id] / the_device.t_duration
        else:
            return Constraint.Skip
    m.c_max_storage_output = Constraint(m.set_storage,  m.t_8760, rule = c_max_storage_output)

    #def c_storage_discharge_flag(model, storage_id,  t):
    #    m = model
    #    return m.storage_discharge_power[storage_id, t] <= big_M * m.storage_discharge_flag[storage_id,  t]
    #m.c_storage_discharge_flag = Constraint(m.set_storage,  m.t_8760, rule = c_storage_discharge_flag)
    
    def c_max_storage_cap(model, storage_id,  t):
        m = model
        return m.storage_soc[storage_id, t] <= m.storage_invest[storage_id]
    m.c_max_storage_cap = Constraint(m.set_storage, m.t_8760, rule = c_max_storage_cap)
    
    #def c_mutual_exclusive(model, storage_id, t):
    #    m = model
    #    return m.storage_charge_flag[storage_id, t] + m.storage_discharge_flag[storage_id, t] <= 1
    #m.c_mutual_exclusive = Constraint(m.set_storage, m.t_8760, rule = c_mutual_exclusive)
    
    #----------------------------------------
    # 季节性储能是否投建的0-1约束
    def c_seasonal_heat_storage(model):
        m = model
        # 找到季节性热储能设备的索引
        for storage_id, device in enumerate(m.storage_device_list):
            if device.label == "Seasonal_Heat_Storage":
                return m.storage_invest[storage_id] <= big_M * m.seasonal_heat_storage_used
        return Constraint.Skip
    m.c_seasonal_heat_storage = Constraint(rule=c_seasonal_heat_storage)

    #----------------------------------------
    #定义投资的光伏发电/太阳能集热器的约束
    m.solar_Area = Var([0, 1], within=NonNegativeReals,initialize=0)
    def c_solar_invest(model):
        m = model
        return m.solar_Area[0] + m.solar_Area[1] <= m.pv_space
    m.c_solar_invest = Constraint(rule=c_solar_invest)
    # 能量母线约束
    # 首先定义能源类型
    m.set_energy_kind = Set(initialize=["elec", "heat", "cold", "gas"])
    m.set_buy_energy = Set(initialize=["elec", "gas"])
    m.set_solar_energy = Set(initialize=["elec", "heat"])
    m.set_shed_energy = Set(initialize=["elec", "heat", "cold"])
    # 定义购电的决策变量
    m.buy_energy = Var(m.set_buy_energy, m.t_8760, within = NonNegativeReals)
    # 定义弃负荷的决策变量
    m.shed_energy = Var(m.set_energy_kind, m.t_8760, within = NonNegativeReals)
    # 定义光伏发电/太阳能集热量的决策变量

    # 定义光伏发电/太阳能集热量的决策变量
    m.solar_energy = Var(m.set_solar_energy, m.t_8760, within=NonNegativeReals)

    # 定义光伏发电和太阳能集热器的约束
    def c_solar_energy_elec(model, t):
        m = model
        return m.solar_energy["elec", t] <= m.solar_Area[0] * m.solar_device_list[0].efficiency[0] * m.pv_I[t] * m.solar_device_list[0].area_rate

    def c_solar_energy_heat(model, t):
        m = model
        return m.solar_energy["heat", t] <= m.solar_Area[1] * m.solar_device_list[1].efficiency[0] * m.pv_I[t] * m.solar_device_list[1].area_rate

    m.c_solar_energy_elec = Constraint(m.t_8760, rule=c_solar_energy_elec)
    m.c_solar_energy_heat = Constraint(m.t_8760, rule=c_solar_energy_heat)

    # 然后定义能源平衡约束
    def c_bus_balance(model, energy_kind, t):
        m = model
        
        # 首先定义总产能源的变量
        total_output = 0
        # 购电，看是否是气和电
        if energy_kind == "elec" or energy_kind == "gas":
            total_output += m.buy_energy[energy_kind, t]
        # 光伏发电或太阳能集热器
        if energy_kind == "elec":
            total_output += m.solar_energy["elec", t]
        elif energy_kind == "heat":
            total_output += m.solar_energy["heat", t]
        # 能源转换设备
        for device in m.conversion_device_list:
            if energy_kind == device.input_kind:
                input_key = device.label + "_" + energy_kind
                total_output -= m.convert_power[input_key, t]
            elif energy_kind in device.output_kind:
                output_key = device.label + "_" + energy_kind
                total_output += m.convert_power[output_key, t]
        
        # 储能设备
        for device_id in range(len(m.storage_device_list)):
            the_device = m.storage_device_list[device_id]
            # 跳过季节性热储，因为季节性热储从热泵那里接收和输出能量
            if the_device.label == "Seasonal_Heat_Storage":
                continue
            if energy_kind == the_device.input_kind:
                total_output += m.storage_discharge_power[device_id, t] - m.storage_charge_power[device_id, t]
        
        # 根据能源类型返回不同的约束
        if energy_kind == "elec":
            return total_output + m.shed_energy["elec", t] == m.elec_load[t]
        elif energy_kind == "heat":
            return total_output + m.shed_energy["heat", t] == m.heat_load[t] + m.seasonal_heat_storage_heating[t]
        elif energy_kind == "cold":
            return total_output + m.shed_energy["cold", t] == m.cold_load[t] + m.seasonal_heat_storage_cooling[t]
        elif energy_kind == "gas":
            return total_output == 0
    
    m.c_bus_balance = Constraint(m.set_energy_kind, m.t_8760, rule=c_bus_balance)
    #----------------------------------------
    # 目标函数相关
    m.total_cost = Var(within = NonNegativeReals)
    # 首先计算总投资成本
    invest_cost = 0
    for device_id in range(len(m.conversion_device_list)):
        the_device = m.conversion_device_list[device_id]
        invest_cost += the_device.cost * m.convert_invest[device_id]
        # 储能设备
    for device_id in range(len(m.storage_device_list)):
        the_device = m.storage_device_list[device_id]
        if the_device.label == "Seasonal_Heat_Storage":
            invest_cost += old_equal(116.32, 30) * m.seasonal_heat_storage_used + the_device.cost * m.storage_invest[device_id]
        else:
            invest_cost += the_device.cost * m.storage_invest[device_id]
        # 光伏发电/太阳能集热器
        invest_cost += pv.cost * (m.solar_Area[0] * m.solar_device_list[0].area_rate)
        invest_cost += sc.cost * (m.solar_Area[1] * m.solar_device_list[1].area_rate)
    m.invest_cost = invest_cost
    # 然后计算运行成本
    # 定义目标函数
    def c_objective(model):
        m = model
        #------------------------------------------------
        # 容量成本
        invest_cost = 0
        # 转换设备
        for device_id in range(len(m.conversion_device_list)):
            the_device = m.conversion_device_list[device_id]
            invest_cost += the_device.cost * m.convert_invest[device_id]
        # 储能设备
        for device_id in range(len(m.storage_device_list)):
            the_device = m.storage_device_list[device_id]
            if the_device.label == "Seasonal_Heat_Storage":
                invest_cost += old_equal(0, 30) * m.seasonal_heat_storage_used + the_device.cost * m.storage_invest[device_id]
            else:
                invest_cost += the_device.cost * m.storage_invest[device_id]
        # 光伏发电/太阳能集热器
        invest_cost += pv.cost * (m.solar_Area[0] * m.solar_device_list[0].area_rate)
        invest_cost += sc.cost * (m.solar_Area[1] * m.solar_device_list[1].area_rate)
        #------------------------------------------------
        # 运行成本
        oper_cost = 0
        for t in m.t_8760:
            # 统一为万元单位
            # 购电成本
            oper_cost += m.elec_price[t] * m.buy_energy["elec", t] / 10000
            oper_cost += m.gas_price[t] * m.buy_energy["gas", t] / 10000
            # 弃负荷成本
            oper_cost += m.shed_energy["elec", t] * 1e3
            oper_cost += m.shed_energy["heat", t] * 1e3
            oper_cost += m.shed_energy["cold", t] * 1e3
            #碳排放成本
            oper_cost += m.carbon_price * m.elec_carbon[t] * m.buy_energy["elec", t] / 10000
            oper_cost += m.carbon_price * gas_carbon * m.buy_energy["gas", t] / 10000

        # 全年运行成本
        total_cost = invest_cost + oper_cost
        return m.total_cost == total_cost
    m.c_objective = Constraint(rule = c_objective)
    m.carbon_cost = 0
    for t in m.t_8760:
        m.carbon_cost += m.carbon_price * m.elec_carbon[t] * m.buy_energy["elec", t] / 10000
        m.carbon_cost += m.carbon_price * gas_carbon * m.buy_energy["gas", t] / 10000

    # 定义目标函数
    m.objective = Objective(expr = m.total_cost, sense = minimize)

    #----------------------------------------
    #求解
    #print('Construction Complete. {}s used. Optimizing...'.format(time.time()-start_time))
    start_time = time.time()
    opt = SolverFactory('gurobi') 
    solution = opt.solve(m)
    #print('Optimization Complete. {}s used.'.format(time.time()-start_time))

    return m

if __name__ == '__main__':
    carbon_price = 600
    pv_space = 3.8
    # 选择城市
    # 选择工艺
    city_codes = [1, 2, 3, 4]
    city_map = {
    1: "Beijing",
    2: "Guangzhou",
    3: "Wuhan",
    4: "Wulumuqi"
}
    # 选择负荷
    load = 'heat'
    # 选择规模
    scale = 0
    #打印季节性热储能规划结果
    for i in city_codes:
        m = optimal_plan(i, carbon_price, pv_space, load, scale)
        print(f'City: {city_map[i]}')

        for device_id, device in enumerate(m.storage_device_list):
            if device.label == "Seasonal_Heat_Storage":
                print(f"Seasonal Heat Storage: {m.storage_invest[device_id].value}")
