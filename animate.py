"""
A simple example of an animated plot
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx

import loader
import analyze

def transitionPositions(pos1, pos2, alpha):
    return {n: (1-alpha)*pos1[n] + alpha*pos2[n] for n in pos1.keys()}

def mst(G):
    return nx.algorithms.tree.minimum_spanning_tree(G)

data = loader.loadAllAndClean("gpw_2007_list.txt")
networks = analyze.createNetworksSeriesWithCount(data, 10)

positions = None
fig, ax  = plt.subplots()

network_index = -1
FRAMES_PER_TRANSITION=20
def animate(i):
    global G_old
    global G_new
    global pos_old
    global pos_new
    global network_index
    global alpha
    if(i == 0):
        G_new = mst(networks[0])
        pos_new = nx.spring_layout(G_new)
    if(i%FRAMES_PER_TRANSITION == 0):
        network_index+=1
        G_old = G_new
        pos_old = pos_new
        G_new = mst(networks[network_index+1])
        pos_new = nx.spring_layout(G_new)
        alpha = 0.
    ax.clear()
    nx.draw(G_old if i<(FRAMES_PER_TRANSITION/2) else G_new, pos=transitionPositions(pos_old, pos_new, alpha), ax=ax)
    alpha +=1./FRAMES_PER_TRANSITION
    return ax,

ani = animation.FuncAnimation(fig, animate, np.arange(10*FRAMES_PER_TRANSITION),
                              interval=25, blit=True)
plt.show()
