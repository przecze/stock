import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import analyze
import loader
import datetime
import scipy.stats as sts
from matplotlib import animation
def mst(G):
    return nx.algorithms.tree.mst.minimum_spanning_tree(G)

x = [] # aniamacja będzie korzystała z tych list - najpierw entropy() je wypełni, a dopiero potem będzie rysowana animacja
y = []

def entropy():
    data = loader.loadAllAndClean("gpw_2007_list.txt")
    networks = analyze.createNetworksSeries(data, start_date=datetime.date(year=2005, month=1, day=1), end_date=datetime.date(year=2009, month=12, day=31))
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
        for n in distance.index:
            for j in distance.index:
                if n != j:
                    if G.has_edge(n,j):
                        continue
                    else:
                        G.add_edge(n,j,weight = distance[n][j])
        try:
            network2 = mst(G)
            for n in network2.nodes():
                for j in network2.nodes():
                    if n != j:
                        if distance[n][j] not in apex:
                            if distance[j][n] not in apex:
                                apex.append(distance[n][j])
            entrop = sts.entropy(apex) #próbowałem policzyć to "ręcznie" - wychodzi tak samo, ale wartości oscylują w okolicy 0,5, więc tu jest bliżej tego co na wykładzie
        except ValueError:
            entrop = y[-1]
        y.append(entrop)
        a+=1
fig = plt.figure()
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('Entropy')

ax = plt.subplot(1,1,1)

def animate(i):
    xs = x[:i]
    ys = y[:i]
    ax.clear()
    ax.plot(xs, ys)
    return ax.plot(xs,ys)
entropy()
ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()
