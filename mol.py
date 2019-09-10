import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import analyze
import loader
import datetime
from matplotlib import animation

def mst(G):
    return nx.algorithms.tree.mst.minimum_spanning_tree(G)

x = []
y = []

def mol():
    data = loader.loadAllAndClean("gpw_2007_list.txt")
    networks = analyze.createNetworksSeries(data, start_date=datetime.date(year=2005, month=1, day=3), end_date=datetime.date(year=2009, month=12, day=31))
    dates = pd.DatetimeIndex(networks.index)
    a = 0
    for i in dates:
        G = nx.Graph()
        apex = []
        x.append(i)
        if a < 30:
            distance = analyze.calculateDistances(data[a:a + 30])
        else:
            distance = analyze.calculateDistances(data[a-15:a+15])
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
            for l in nx.degree(network2):
                apex.append(l[0])
            q =  max(nx.degree_centrality(network2).values())
            for key in nx.degree_centrality(network2).keys():
                if nx.degree_centrality(network2)[key] == q:
                    center = key
            way = 0
            for e in apex:
                way += len(nx.shortest_path(network2,center,e)) -1
            mol = way//len(apex)
        except ValueError:
            mol = y[-1]
        y.append(mol)

fig = plt.figure()
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('mol')

ax = plt.subplot(1,1,1)

def animate(i):
    xs = x[:i]
    ys = y[:i]
    ax.clear()
    ax.plot(xs, ys)
    return ax.plot(xs,ys)
mol()
ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()