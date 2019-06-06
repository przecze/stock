"""
A simple example of an animated plot
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# https://stackoverflow.com/questions/17558096/animated-title-in-matplotlib
def _blit_draw(self, artists, bg_cache):
    # Handles blitted drawing, which renders only the artists given instead
    # of the entire figure.
    updated_ax = []
    for a in artists:
        # If we haven't cached the background for this axes object, do
        # so now. This might not always be reliable, but it's an attempt
        # to automate the process.
        if a.axes not in bg_cache:
            # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            # change here
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        # ax.figure.canvas.blit(ax.bbox)
        ax.figure.canvas.blit(ax.figure.bbox)

# MONKEY PATCH!!
matplotlib.animation.Animation._blit_draw = _blit_draw

#

import networkx as nx
import pandas

import loader
import analyze

def transitionPositions(pos1, pos2, alpha):
    return {n: (1-alpha)*pos1[n] + alpha*pos2[n] for n in pos1.keys()}

def mst(G):
    return nx.algorithms.tree.minimum_spanning_tree(G)

data = loader.loadAllAndClean("gpw_2007_list.txt")
networks = analyze.createNetworksSeriesWithCount(data, 10)
dates = pandas.DatetimeIndex(networks.index)

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
    global date_old
    global date_new
    if(i == 0):
        G_new = mst(networks[0])
        pos_new = nx.spring_layout(G_new)
    if(i%FRAMES_PER_TRANSITION == 0):
        date_old = dates[network_index].date()
        date_new = dates[network_index+1].date()
        network_index+=1
        G_old = G_new
        pos_old = pos_new
        G_new = mst(networks[network_index+1])
        pos_new = nx.spring_layout(G_new, pos=pos_old)
        alpha = 0.
    ax.clear()
    date_str = str(date_old) if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else str(date_new)
    ttl = ax.text(.5, 1.05, date_str, transform = ax.transAxes, va='center')
    nx.draw(G_old if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else G_new, pos=transitionPositions(pos_old, pos_new, alpha), ax=ax, with_labels = True)
    alpha +=1./FRAMES_PER_TRANSITION
    return ax,

ani = animation.FuncAnimation(fig, animate, np.arange(len(networks)*FRAMES_PER_TRANSITION),
                              interval=25, blit=True)
plt.show()
