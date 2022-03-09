import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
import sqlite3

con = sqlite3.connect('/home/nachiket/vizier-scala/vizier.db/Vizier.db')

cur = con.cursor()

# for row in cur.execute(' SELECT c.module_id, c.state, c.created, r.started, r.finished FROM cell c LEFT OUTER JOIN result r ON c.result_id = r.id WHERE c.workflow_id = (SELECT max(id) FROM workflow);'):
#     print(row)

df = pd.read_sql("SELECT c.module_id, c.state, strftime('%H%M%S',time(c.created/10, 'unixepoch')) as created, strftime('%H%M%S',time(r.started/10,'unixepoch')) as started, strftime('%H%M%S',time(r.finished/10,'unixepoch')) as finished FROM cell c LEFT OUTER JOIN result r ON c.result_id = r.id WHERE c.workflow_id = (SELECT max(id) FROM workflow)", con)

print(df)

bars_1 = df['created'].astype('int')
bars_2 = df['started'].astype('int')
bars_3 = df['started'].astype('int')

print(bars_1)
print(bars_2)
print(bars_3)

bars = np.add(bars_1, bars_2).tolist()

print(bars)


r = [i for i in range(0,len(bars_1))]

names = [module for module in df['module_id']]
barWidth = 1

# Create brown bars
plt.bar(r, bars_1, color='green', edgecolor='white', width=barWidth)
# Create green bars (middle), on top of the first ones
plt.bar(r, bars_2, bottom=bars_1, color='orange', edgecolor='white', width=barWidth)
# Create green bars (top)
plt.bar(r, bars_3, bottom=bars, color='blue', edgecolor='white', width=barWidth)


plt.xticks(r, names, fontweight='bold')
plt.xlabel("Modules")

plt.savefig('Task_chart_Parallel')

#print(df['created'])


