import pandas as pd
import plotly.graph_objects as go
import os

def read_data(file_path):
    return pd.read_csv(file_path)

def create_sankey_plot_from_csv(csv_file_path, city_name):
    # 读取数据
    flow_data = read_data(csv_file_path)

    # 创建数据框
    pdata = flow_data

    # 创建节点名称数据框
    nodes = pd.DataFrame({'name': pd.concat([pdata['source'], pdata['target']]).unique()})

    # 把source、target转换为数字
    pdata['IDsource'] = pdata['source'].apply(lambda x: nodes[nodes['name'] == x].index[0])
    pdata['IDtarget'] = pdata['target'].apply(lambda x: nodes[nodes['name'] == x].index[0])

    # 定义颜色分组
    def get_group(source, target):
        if source == "gas":
            return "group1"
        elif source in ["elc_input", "elec", "CHP"]:
            return "group2"
        elif source in ["CHP_heat", "heat_pump", "heat", "Electric_boiler"] or target == "heat_storage":
            return "group3"
        elif source in ["CERG", "WARP", "cold"] or target == "cold_storage":
            return "group4"
        elif source == "heat_storage" or target == "heat_storage":
            return "heat_storage"
        elif source == "cold_storage" or target == "cold_storage":
            return "cold_storage"
        else:
            return "group5"

    pdata['group'] = pdata.apply(lambda row: get_group(row['source'], row['target']), axis=1)

    # 定义节点颜色
    node_colors = []
    for name in nodes['name']:
        if name in ["gas"]:
            color = "#ff7f0e"  # 橙色
        elif name in ["elc_input", "elec", "CHP"]:
            color = "#2ca02c"  # 绿色
        elif name in ["CHP_heat", "heat_pump", "heat"] or name == "heat_storage":
            color = "#d62728"  # 红色
        elif name in ["CERG", "WARP", "cold"] or name == "cold_storage":
            color = "#1f77b4"  # 蓝色
        else:
            color = "black"
        node_colors.append(color)

    # 计算每个节点的汇入流和输出流的总和
    node_inflows = pdata.groupby('IDtarget')['weight'].sum()
    node_outflows = pdata.groupby('IDsource')['weight'].sum()

    # 创建新的节点标签，包含节点名称和汇入流或输出流的总和
    # node_labels = []
    # for i, name in enumerate(nodes['name']):
    #     if name in ["elc_input", "gas", "pv"]:
    #         outflow = node_outflows[i] if i in node_outflows else 0
    #         node_labels.append(f"{name}\n {outflow:.2f} MWH")
    #     else:
    #         inflow = node_inflows[i] if i in node_inflows else 0
    #         node_labels.append(f"{name}\n {inflow:.2f} MWH")
# ...existing code...
    node_labels = []
    for i, name in enumerate(nodes['name']):
        if name in ["elecinput", "gas", "PV"]:
            outflow = node_outflows[i] if i in node_outflows else 0
            node_labels.append(f"{name}\n outflow: {outflow:.2e} MWH")
        elif name in ["elec_load", "heat_load", "cold_load"]:
            inflow = node_inflows[i] if i in node_inflows else 0
            node_labels.append(f"{name}\n inflow: {inflow:.2e} MWH")
        elif name in ["elec", "heat", "cold"]:
            node_labels.append(f" ")
        else:
            inflow = node_inflows[i] if i in node_inflows else 0
            outflow = node_outflows[i] if i in node_outflows else 0
            node_labels.append(f"{name}\n inflow: {inflow:.2e} MWH\n outflow: {outflow:.2e} MWH")
# ...existing code...
    # 正式绘图---------------------------------------
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=50,  # 增加节点之间的间距
            thickness=50,  # 默认厚度
            line=dict(color="black", width=0.01),
            label=node_labels,  # 使用新的节点标签
            color=node_colors
        ),
        link=dict(
            source=pdata['IDsource'],
            target=pdata['IDtarget'],
            value=pdata['weight'],
            color=pdata.apply(lambda row: (
                "#8B0000" if row['source'] in ["Seasonal_Heat_Storage","Heat_Storage"] else
                "#d62728" if row['source'] in ["Gas_Boiler", "Heat_Pump"] else
                "#00008B" if row['source'] == "Cold_Storage" else
                "#2ca02c" if row['source'] == "PV" else
                "#ff7f0e" if row['source'] == "gas" else
                "#1f77b4" if row['source'] in ["cold","WARP","CERG","Ground_Heat_Pump_cold", "Gas_Heat_Pump_cold"] else
                "#d62728" if row['source'] in ["heat","Electric_Boiler","Ground_Heat_Pump_heat","Gas_Heat_Pump_heat"] else
                "#2ca02c" if row['source'] in ["elec","elecinput"] else
                "#006400"
            ), axis=1),
            label=pdata['weight'].astype(str),
            hovertemplate='Value: %{value:.2f} units<extra></extra>'
        )
    )])

    fig.update_layout(title_text=f"{city_name} Sankey Diagram", font_size=10)

    # 保存
    output_dir = './plots/sankey_plots'
    os.makedirs(output_dir, exist_ok=True)
    fig.write_html(os.path.join(output_dir, f"{city_name}_sankey.html"))
    fig.write_image(os.path.join(output_dir, f"{city_name}_sankey.png"))
    fig.write_image(os.path.join(output_dir, f"{city_name}_sankey.pdf"))

if __name__ == '__main__':
    city_files = {
        "Beijing": "/Users/liuboyuan/Desktop/ploting/plots/sankey_plots/Beijing_generated_flow_data.csv",
        "Guangzhou": "/Users/liuboyuan/Desktop/ploting/plots/sankey_plots/Guangzhou_generated_flow_data.csv",
        "Wuhan": "/Users/liuboyuan/Desktop/ploting/plots/sankey_plots/Wuhan_generated_flow_data.csv",
        "Wulumuqi": "/Users/liuboyuan/Desktop/ploting/plots/sankey_plots/Wulumuqi_generated_flow_data.csv"
    }
    
    for city_name, csv_file_path in city_files.items():
        create_sankey_plot_from_csv(csv_file_path, city_name)