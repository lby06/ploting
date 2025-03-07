import matplotlib.pyplot as plt
import pandas as pd
import os
from optimal_plan import optimal_plan

def plot_energy_data(model, city_name):
    # 提取8760小时的数据
    hours = list(range(8760))
    
    # 创建一个字典来存储每种能源的输入数据
    energy_data = {
        "gas": [model.buy_energy["gas", t]() for t in hours],
        "elec": [
            model.buy_energy["elec", t]() + 
            sum(model.convert_power[f"{device.label}_elec", t]() for device in model.conversion_device_list if "elec" in device.output_kind) +
            sum(model.storage_discharge_power[device_id, t]() for device_id, device in enumerate(model.storage_device_list) if device.output_kind == "elec") -
            sum(model.storage_charge_power[device_id, t]() for device_id, device in enumerate(model.storage_device_list) if device.input_kind == "elec")
            for t in hours
        ],
        "heat": [
            sum(model.convert_power[f"{device.label}_heat", t]() for device in model.conversion_device_list if "heat" in device.output_kind) +
            sum(model.storage_discharge_power[device_id, t]() for device_id, device in enumerate(model.storage_device_list) if device.output_kind == "heat") -
            sum(model.storage_charge_power[device_id, t]() for device_id, device in enumerate(model.storage_device_list) if device.input_kind == "heat")
            for t in hours
        ],
        "cold": [
            sum(model.convert_power[f"{device.label}_cold", t]() for device in model.conversion_device_list if "cold" in device.output_kind) +
            sum(model.storage_discharge_power[device_id, t]() for device_id, device in enumerate(model.storage_device_list) if device.output_kind == "cold") -
            sum(model.storage_charge_power[device_id, t]() for device_id, device in enumerate(model.storage_device_list) if device.input_kind == "cold")
            for t in hours
        ]
    }

    # 创建一个DataFrame来存储数据
    df = pd.DataFrame(energy_data, index=hours)

    # 打印前24小时的数据
    print(f"{city_name} 前24小时的数据:")
    print(df.head(24))

    # 创建输出目录
    output_dir = './plots/energy_plots'
    os.makedirs(output_dir, exist_ok=True)

    # 将前24小时的数据保存到同一个CSV文件中
    output_file = os.path.join(output_dir, f'{city_name}_first_24_hours_energy_data.csv')
    df.head(24).to_csv(output_file)
    print(f"First 24 hours energy data for {city_name} saved to {output_file}")

    # 为每种能源单独绘制图像并保存
    for energy_type in df.columns:
        plt.figure(figsize=(30, 10))  # 调整图像大小
        plt.plot(df.index, df[energy_type], label=energy_type)
        plt.xlabel('Hours')
        plt.ylabel('Energy (MW)')
        plt.title(f'{city_name} - {energy_type.capitalize()} Energy Over 8760 Hours')
        plt.legend()
        plt.grid(True)
        plt.ylim(df[energy_type].min(), df[energy_type].max())
        plt.yticks(range(int(df[energy_type].min()), int(df[energy_type].max()) + 1))
        plt.xticks(range(0, 8760, 1))
        # 保存图像
        image_file = os.path.join(output_dir, f'{city_name}_{energy_type}_energy.png')
        plt.savefig(image_file)
        print(f"Plot for {city_name} - {energy_type} saved to {image_file}")
        plt.close()

if __name__ == '__main__':
    city_codes = [1, 2, 3, 4]
    city_names = ["Beijing", "Guangzhou", "Wuhan", "Wulumuqi"]
    
    for city_code, city_name in zip(city_codes, city_names):
        m = optimal_plan(city_code)
        plot_energy_data(m, city_name)