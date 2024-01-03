import pandas as pd
import matplotlib.pyplot as plt


files = ['result/values_result.csv',
         'result/values_add_commision'
         ]

df = pd.read_csv(files[0], names=['x','y','z'])

print(df)

x = df['x'].values
y = df['y'].values
z = df['z'].values

fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_trisurf(x, y, z, cmap='viridis', edgecolor='k')

fig.colorbar(surf)

ax.set_xlabel('change position day')
ax.set_ylabel('pct_change_period')
ax.set_zlabel('value')
plt.savefig('./result/value.png')
plt.show()
