import pandas as pd

def calculate_flows(file_path):
    # 读取数据文件
    df = pd.read_csv(file_path)

    # 计算流入和流出 cold 节点的总和
    cold_inflow = df[df['target'] == 'cold']['weight'].sum()
    cold_outflow = df[df['source'] == 'cold']['weight'].sum()

    # 计算流入和流出 heat 节点的总和
    heat_inflow = df[df['target'] == 'heat']['weight'].sum()
    heat_outflow = df[df['source'] == 'heat']['weight'].sum()

    return cold_inflow, cold_outflow, heat_inflow, heat_outflow

if __name__ == '__main__':
    file_path = '/Users/liuboyuan/Desktop/ploting/plots/sankey_plots/generated_flow_data.csv'
    cold_inflow, cold_outflow, heat_inflow, heat_outflow = calculate_flows(file_path)

    print(f"Cold Inflow: {cold_inflow}")
    print(f"Cold Outflow: {cold_outflow}")
    print(f"Heat Inflow: {heat_inflow}")
    print(f"Heat Outflow: {heat_outflow}")