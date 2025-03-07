
# with seasonal_heat_storage
# City Name: Beijing
# Elec Bus Cost: 0.0740050407576784
# Heat Bus Cost: 0.03678065627954413
# Cold Bus Cost: 0.015504770796289443

# City Name: Guangzhou
# Elec Bus Cost: 0.07156772913961354
# Heat Bus Cost: 0.06038374796131477
# Cold Bus Cost: 0.014678442267339577

# City Name: Wuhan
# Elec Bus Cost: 0.07474419094825296
# Heat Bus Cost: 0.036880673045598666
# Cold Bus Cost: 0.015531883893331733

# City Name: Wulumuqi
# Elec Bus Cost: 0.08092289814436694
# Heat Bus Cost: 0.03953742801397417
# Cold Bus Cost: 0.015970760447910577


#witout seasonal_heat_storage
# City Name: Beijing
# Elec Bus Cost: 0.07320005984271724
# Heat Bus Cost: 0.036215524423166306
# Cold Bus Cost: 0.016363916782113304

# City Name: Guangzhou
# Elec Bus Cost: 0.07198721560241139
# Heat Bus Cost: 0.06318286993398815
# Cold Bus Cost: 0.014799578174733674

# City Name: Wuhan
# Elec Bus Cost: 0.0754451509351623
# Heat Bus Cost: 0.0368480942771715
# Cold Bus Cost: 0.015827474427956394

# City Name: Wulumuqi
# Elec Bus Cost: 0.08109164222666997
# Heat Bus Cost: 0.039360415869802254
# Cold Bus Cost: 0.01787518151525414
import matplotlib.pyplot as plt
import numpy as np

# Data
cities = ["Beijing", "Guangzhou", "Wuhan", "Wulumuqi"]
elec_with_ss = [0.0740050407576784, 0.07156772913961354, 0.07474419094825296, 0.08092289814436694]
heat_with_ss = [0.03678065627954413, 0.06038374796131477, 0.036880673045598666, 0.03953742801397417]
cold_with_ss = [0.015504770796289443, 0.014678442267339577, 0.015531883893331733, 0.015970760447910577]

elec_without_ss = [0.07320005984271724, 0.07198721560241139, 0.0754451509351623, 0.08109164222666997]
heat_without_ss = [0.036215524423166306, 0.06318286993398815, 0.0368480942771715, 0.039360415869802254]
cold_without_ss = [0.016363916782113304, 0.014799578174733674, 0.015827474427956394, 0.01787518151525414]

# Plotting
x = np.arange(len(cities))  # the label locations
width = 0.15  # the width of the bars

fig, ax = plt.subplots(figsize=(12, 8))

rects1 = ax.bar(x - width*1.5, elec_with_ss, width, label='Elec with SS')
rects2 = ax.bar(x - width/2, elec_without_ss, width, label='Elec without SS')
rects3 = ax.bar(x + width/2, heat_with_ss, width, label='Heat with SS')
rects4 = ax.bar(x + width*1.5, heat_without_ss, width, label='Heat without SS')
rects5 = ax.bar(x + width*2.5, cold_with_ss, width, label='Cold with SS')
rects6 = ax.bar(x + width*3.5, cold_without_ss, width, label='Cold without SS')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_xlabel('Cities')
ax.set_ylabel('Cost (million RMB/MW)')
ax.set_title('Cost Comparison with and without Seasonal Heat Storage')
ax.set_xticks(x)
ax.set_xticklabels(cities)
ax.legend()

# Add labels
def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(round(height, 4)),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
autolabel(rects4)
autolabel(rects5)
autolabel(rects6)

fig.tight_layout()

plt.show()