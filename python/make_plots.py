import matplotlib.pylab as plt
import numpy as np
from generate_db import load_papers
from utils import paper_network, authSimple
import networkx as nx

import sys
sys.path.append("/Users/yoachim/gitRepos/matplotlib_pubplots/python")
import set_plot_params as spp

def plot_example_networks():
    """
    Plot an example ADS entry network
    """
    figs = []
    filenames = []
    bibcodes = ['2007PhDT.........3Y', '2011PhDT.......139B',
                '2002PhDT........15W', '2010PhDT.......132W',
                '2012PhDT.......311C']
    files = ['output/'+bibcode[:4]+'/'+bibcode.replace('.','_')+'.npz' for bibcode in bibcodes]
    texts = ['(a)', '(b)','(c)', '(d)','(e)']

    count = 0
    for bibcode,filename,text in zip(bibcodes, files,texts):
        fig,ax = plt.subplots()
        figDummy, axDummy = plt.subplots()

        papers, flags = load_papers(filename)
        phd = [paper for paper in papers if paper['bibcode'] == bibcode][0]
        connected_papers, network = paper_network(papers, phd, authSimple(phd['author'][0]))
        years = []
        for node in network.nodes():
            years.append(float(node[0:4]))

        # Make the graph repeatable
        pos = {}
        for i, node in enumerate(network.nodes()):
            pos[node] = (years[i],i**2)
        layout = nx.spring_layout(network, pos=pos)

        nx.draw_networkx(network, pos=layout, ax=ax, node_size=100,
                         node_color=years, alpha=0.5, with_labels=False)
        mappableDummy = axDummy.scatter(years,years,c=years)
        cbar = plt.colorbar(mappableDummy, ax=ax, format='%i')
        cbar.set_label('Year')
        ax.text(.1,.8, text, fontsize=24, transform=ax.transAxes)
        ax.set_axis_off()
        figs.append(fig)
        filenames.append('example_network_%i' %count)
        count += 1
    return figs, filenames

if __name__ == '__main__':

    funcs = []
    kwargs = []

    funcs.append(plot_example_networks)
    kwargs.append({})

    spp.plot_multi_format(funcs, plot_kwargs=kwargs,
                          usetex=False, outdir='../plots')
