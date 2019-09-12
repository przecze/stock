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
import datetime
import pandas
import scipy.stats as sts
import loader
import analyze

def averageDict(d1: dict, d2: dict, alpha):
    return {n: (1-alpha)*d1[n] + alpha*d2[n] for n in d1.keys()}

def mst(G):
    return nx.algorithms.tree.mst.minimum_spanning_tree(G)

data = loader.loadCountAndClean("gpw_2007_list.txt", 30)
networks = analyze.createNetworksSeries(data, start_date=datetime.date(year=2007, month=12, day=1), end_date=datetime.date(year=2009, month=1, day=1))
dates = pandas.DatetimeIndex(networks.index)

positions = None
fig = plt.figure()
gs = matplotlib.gridspec.GridSpec(2, 1, height_ratios = [3, 1])
ax_graph  = fig.add_subplot(gs[0])
ax_plot = fig.add_subplot(gs[1])
#values
ent = [] #entropy
ent_eff = [] # entropy_efficient
molemem = [] #mol

FRAMES_PER_TRANSITION=10
def animate(i):
    global G_old
    global G_new
    global pos_old
    global pos_new
    global alpha
    global date_old
    global date_new
    global widths_new
    global widths_old
     global entrop
    global mol
    global entrop_efficient
    if(i == 0):
        G_new = mst(networks[0])
        pos_new = nx.spring_layout(G_new, k=2./np.sqrt(len(G_new.nodes)))
        widths_new = [1/G_new[u][v]['weight'] for u, v in G_new.edges()]
    if(i%FRAMES_PER_TRANSITION == 0):
        network_index = i//FRAMES_PER_TRANSITION
        date_old = dates[network_index].date()
        date_new = dates[min(network_index+1, len(dates)-1)].date()
        G_old = G_new
        pos_old = pos_new
        widths_old = widths_new
        G_new = mst(networks[min(network_index+1, len(networks)-1)])
        pos_new = nx.spring_layout(G_new, k=2./np.sqrt(len(G_new.nodes)), pos=pos_old)
        widths_new = [1/G_new[u][v]['weight'] for u, v in G_new.edges()]
        alpha = 0.
        #zwykła entropia
        network2 = G_new
        apex1 = []
        apex2 = []
        for l in nx.degree(network2):
            apex1.append(l[1])
        entrop = sts.entropy(apex1)
        #mol
        for l in nx.degree(network2):
            apex2.append(l[0])
        center = ['',0]
        for r in network2.nodes():
            if nx.degree(network2,r) > center[1]:
                center = [r,nx.degree(network2,r)]
        way = 0
        for e in apex2:
            way += len(nx.shortest_path(network2,center[0],e)) -1
        mol = way//len(apex2)
        #entropy_efficient
        entrop_efficient = sts.entropy(widths_new)
    ax_graph.clear()
    ax_plot.clear()
    date_str = str(date_old) if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else str(date_new)
    ttl = ax_graph.text(.5, 1.05, date_str, transform = ax_graph.transAxes, va='center')

    G_to_draw = G_old if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else G_new
    pos_to_draw = averageDict(pos_old, pos_new, alpha)
    widths_to_draw = widths_old if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else widths_new
    plt.sca(ax_graph) # workaround for bug in nx.draw

    nx.draw_networkx_nodes(G_to_draw, pos=pos_to_draw, ax=ax_graph, node_size=500, node_color='lightgreen', edgecolor='black')

    nx.draw_networkx_edges(G_to_draw, pos=pos_to_draw, ax=ax_graph, edge_color='green', width=10*widths_to_draw)

    nx.draw_networkx_labels(G_to_draw, pos=pos_to_draw, ax=ax_graph, font_weigth='bold')

    ax_plot.plot(pandas.concat(ent))
    ax_plot.plot(pandas.concat(molemem))
    ax_plot.plot(pandas.concat(ent_eff))
    ax_plot.set_xlim(dates[0], dates[-1])
    ax_plot.get_xaxis().set_visible(True)
    ax_plot.get_yaxis().set_visible(True)
    alpha +=1./FRAMES_PER_TRANSITION
    return (ax_plot, ax_graph, ttl)

ani = animation.FuncAnimation(fig, animate, frames=len(networks)*FRAMES_PER_TRANSITION,
                              interval=10, blit=True)
#ani.save('./gif/animation.gif', writer='imagemagick', fps=60)

plt.show()
