import numpy as np
import matplotlib.pyplot as plt
import analyze
import networkx as nx
import loader
import pandas as pd
import datetime
def mst(G):
    return nx.algorithms.tree.mst.minimum_spanning_tree(G)

z = {}

def distribution():
    data = loader.loadAllAndClean("gpw_2007_list.txt")
    networks = analyze.createNetworksSeries(data, start_date=datetime.date(year=2005, month=1, day=3), end_date=datetime.date(year=2009, month=12, day=31))
    dates = pd.DatetimeIndex(networks.index)
    a = 0
    for i in dates:
        G = nx.Graph()
        if a < 40:
            distance = analyze.calculateDistances(data[a:a + 40])
        else:
            distance = analyze.calculateDistances(data[a-20:a+20])
        a +=1
        for n in distance.index:
            for j in distance.index:
                if n != j:
                    if G.has_edge(n,j):
                        continue
                    else:
                        G.add_edge(n,j,weight = distance[n][j])
        try:
            network2 = mst(G)
        except: ValueError

        degrees = [len(list(network2.neighbors(n))) for n in network2.nodes()]
        for r in degrees:
            for s in z.keys():
                if s == r:
                    z[s] +=1
            if r not in z.keys():
                z[r] = 1

distribution()

fig = plt.figure()
ax = plt.subplot(1,1,1)
d = {}
for key in sorted(z):
    d[key] = z[key]
all = 0
x = [i for i in d.keys()]
y = []
for i in d.values():
    all += i
for i in d.values():
    y.append(i/all)
print(x)
print(y)
plt.xlabel('k')
plt.ylabel('f(k)')
plt.title('distribution')
ax.plot(x,y)
plt.show()

