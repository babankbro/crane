import pandas as pd
import math

df = pd.read_csv("./dataset/latlng.csv")
x = df['lat']
y = df['lng']
distance = []
for i in range(len(x)):
    ds = []
    x1 = x[i]
    y1 = y[i]
    
    for j in range(len(y)):
        x2 = x[j]
        y2 = y[j]
        dx = x1 - x2
        dy = y1 - y2
        #print(x1, y1, x2, y2)
        d = math.sqrt(dx*dx + dy*dy)*100
        ds.append(round(d,4))
    ds = [str(d) for d in ds]
    v = ','.join(ds)
    print(f"[ {v}],")
print(df)