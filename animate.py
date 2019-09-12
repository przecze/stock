#!/usr/bin/env python3
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# below is a patch for a problem with matplotlib. You can ignore this code
# see: https://stackoverflow.com/questions/17558096/animated-title-in-matplotlib

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

# patch ends here

import networkx as nx
import datetime
import pandas
import scipy.stats as sts
import loader
import analyze

# helper function for smooth animation - calculates nodes positions in transition frames
def averageDict(d1: dict, d2: dict, alpha):
    return {n: (1-alpha)*d1[n] + alpha*d2[n] for n in d1.keys()}

# reduces the graph
def mst(G):
    return nx.algorithms.tree.mst.minimum_spanning_tree(G)

# load the data from downloaded stooq files and construct correlation networks (for now, full networks, no mst applied)
data = loader.loadCountAndClean("gpw_2007_list.txt", 30)
networks = analyze.createNetworksSeries(data, start_date=datetime.date(year=2007, month=12, day=1), end_date=datetime.date(year=2008, month=12, day=1))
dates = pandas.DatetimeIndex(networks.index)

# prepare subplots for plotting. ax_graph is the area where we visualize the graph (top). ax_plot is the area for plotting how measured values change (bottow)
fig = plt.figure()
gs = matplotlib.gridspec.GridSpec(2, 1, height_ratios = [3, 1])
ax_graph  = fig.add_subplot(gs[0])
ax_plot = fig.add_subplot(gs[1])

#values
ent = [] #entropy
ent_eff = [] # entropy_efficient
molemem = [] #mol

# this means, transition between two steps (two networks) takes 10 frames of animation
FRAMES_PER_TRANSITION=10

# this method will be called every frame by FuncAnimation to update the plot
def animate(i):
    # we'll be changing some global variables, so we need to declare them here
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
        # spring_layout generates positions for the nodes of the graph such that the structure of the graph is best visible
        pos_new = nx.spring_layout(G_new, k=2./np.sqrt(len(G_new.nodes)))
        # we want links representing short distances (strong connection) to be thick. We create array of widths of all edges to pass it to nx.draw
        widths_new = [1/G_new[u][v]['weight'] for u, v in G_new.edges()]
    # at every step (once in every 10 frames): update the network, store the previous one in G_old
    if(i%FRAMES_PER_TRANSITION == 0):
        network_index = i//FRAMES_PER_TRANSITION
        # date_old and date_new are used to display the current date on the top of the animation
        date_old = dates[network_index].date()
        date_new = dates[min(network_index+1, len(dates)-1)].date()
        G_old = G_new
        pos_old = pos_new
        widths_old = widths_new
        # at the very end, network_index == len(networks)-1, we use this to land within array bounds
        G_new = mst(networks[min(network_index+1, len(networks)-1)])
        # we create new positions starting with pos_old. This way the graph won't just spin randomly
        pos_new = nx.spring_layout(G_new, k=2./np.sqrt(len(G_new.nodes)), pos=pos_old)
        widths_new = [1/G_new[u][v]['weight'] for u, v in G_new.edges()]
        # alpha measures the stage of transition. It goes from 0 to 1. during each transition
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
    date_str = str(date_old) if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else str(date_new)

    # draw the current date just over the graph
    ttl = ax_graph.text(.5, 1.05, date_str, transform = ax_graph.transAxes, va='center')

    # for the first part of transition we draw G_old and widths_old, for the second part _new
    G_to_draw = G_old if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else G_new
    pos_to_draw = averageDict(pos_old, pos_new, alpha)
    widths_to_draw = widths_old if i%FRAMES_PER_TRANSITION<(FRAMES_PER_TRANSITION/2) else widths_new

    # workaround for bug in nx.draw
    plt.sca(ax_graph)

    # we draw nodes, edges and labels separately so it's easier to manage the attributes
    nx.draw_networkx_nodes(G_to_draw, pos=pos_to_draw, ax=ax_graph, node_size=500, node_color='lightgreen', edgecolor='black')

    nx.draw_networkx_edges(G_to_draw, pos=pos_to_draw, ax=ax_graph, edge_color='green', width=10*widths_to_draw)

    nx.draw_networkx_labels(G_to_draw, pos=pos_to_draw, ax=ax_graph, font_weigth='bold')

    ax_plot.plot(pandas.concat(ent))
    ax_plot.plot(pandas.concat(molemem))
    ax_plot.plot(pandas.concat(ent_eff))
    ax_plot.set_xlim(dates[0], dates[-1])
    ax_plot.get_xaxis().set_visible(True)
    ax_plot.get_yaxis().set_visible(True)

    # update alpha
    alpha +=1./FRAMES_PER_TRANSITION

    # if blit is True, we have to return objects to redraw in each frame
    return (ax_plot, ax_graph, ttl)

# this starts the animation in a window
ani = animation.FuncAnimation(fig, animate, frames=len(networks)*FRAMES_PER_TRANSITION,
                              interval=10, blit=True, repeat=False)
plt.show()

# if you want to save the animation to gif, use this lines instead (blit has to be False, so it takes longer)

#ani = animation.FuncAnimation(fig, animate, frames=len(networks)*FRAMES_PER_TRANSITION,
#                              interval=10, blit=False, repeat=False)
#ani.save('gif/animation.gif', writer='imagemagick', fps=60)

