import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
import sqlite3
from collections import defaultdict
import matplotlib.patches as mpatches

con = sqlite3.connect('/home/nachiket/vizier-scala/vizier.db/Vizier.db')

cur = con.cursor()

# for row in cur.execute(' SELECT c.module_id, c.state, c.created, r.started, r.finished FROM cell c LEFT OUTER JOIN result r ON c.result_id = r.id WHERE c.workflow_id = (SELECT max(id) FROM workflow);'):
#     print(row)

df = pd.read_sql("SELECT c.module_id, c.state, strftime('%H%M%S',time(c.created/10, 'unixepoch')) as created, strftime('%H%M%S',time(r.started/10,'unixepoch')) as started, strftime('%H%M%S',time(r.finished/10,'unixepoch')) as finished FROM cell c LEFT OUTER JOIN result r ON c.result_id = r.id WHERE c.workflow_id = 30", con)


df['created'] = df['created'].astype('int')
df['started'] = df['started'].astype('int')
df['finished'] = df['finished'].astype('int')


print(df)


fig, gnt = plt.subplots()

colors_dict = defaultdict( CreatetoStart ='Red', StarttoFinish ='Yellow')


gnt.set_xlabel('Time since Notebook Execution')
gnt.set_ylabel('Modules')

gnt.grid(True)


#gnt.broken_barh([(83615,23),(83638,862)],(10, 9), facecolors = ('red','yellow'))

# Setting X-axis limits
gnt.set_xlim((df['created'].iloc[0] - 100), 45000)

gnt.set_ylim(0, 320)
y_ticks = [i for i in range(0,df['created'].count())]
gnt.set_yticklabels(y_ticks)

i = 0
for label, content in df.iterrows():
    print(content['created'],content['started'])
    gnt.broken_barh([(content['created'],(content['started'] - content['created'])),(content['started'], (content['finished'] - content['started'])) ],( i * 30, 9), facecolors =('red','yellow'))
    i += 1 

patches = [mpatches.Patch(color=color, label=key) for (key, color) in colors_dict.items()]
plt.legend(handles=patches,loc='upper right')
plt.savefig("task_chart_serial.png")


