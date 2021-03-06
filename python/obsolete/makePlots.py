#!/usr/bin/env python
import numpy as np
from runYear import readYear
import glob
import matplotlib.pylab as plt
import argparse as arg
import networkx as nx
import ads
from grabPhdClass import phdArticle2row
import sys
sys.path.append("/Users/yoachim/gitRepos/matplotlib_pubplots/python")
import set_plot_params as spp

def retentionCurve(latest_years, phd_years):
    """
    Do the binning to make a curve
    """
    bins = np.arange(0,30,1)-0.5
    years = np.unique(phd_years)

    numberActive = np.zeros((years.size,bins.size),float)
    numberPossible = np.zeros((years.size,bins.size),float)

    lastYearDist = latest_years-phd_years
    for i,year in enumerate(years):
        gg = np.where(phd_years == year)
        droppedHist,bins = np.histogram(lastYearDist[gg],bins)
        droppedHist = np.add.accumulate(droppedHist)
        classSize = gg[0].size
        numberActive[i][0] = classSize
        maxIndex = 2015-year
        numberActive[i][1:maxIndex+1] = classSize-droppedHist[0:maxIndex]
        numberPossible[i][0:maxIndex+1] = classSize

    na = numberActive.sum(axis=0).ravel()
    npos = numberPossible.sum(axis=0).ravel()
    good = np.where(npos > 0)
    curve = na[good]/npos[good]
    return curve,bins[:-1][good]+.5


def linkCheck(firstA=False):
    """
    Check to see if we are over or under-linking papers using the
    unique name flag
    """
    if firstA:
        latest_key = 'latest_1st_year'
    else:
        latest_key = 'latest_year'


    figs = []
    names = []
    data = readYear(0, filename = 'output/all_years.dat')
    # Make a histogram of number of PhDs per year
    good = np.where((data['noAstroJournal'] == 'None') &
                    (data['nonUS'] == 'None'))

    data = data[good]

    binsize = 2
    year_mins = np.arange(1997,2011+binsize,binsize)
    year_maxes = np.arange(1998,2012+binsize,binsize)
    fig,ax = plt.subplots()
    fig2,ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()

    colors = [ plt.cm.jet(x) for x in np.linspace(0, 1, year_mins.size) ]

    for ymin,ymax,color in zip(year_mins,year_maxes,colors):
        good = np.where((data['phd_year'] >= ymin)
                        & (data['phd_year'] <= ymax))

        baseline, bins1 = retentionCurve(data[good][latest_key],data[good]['phd_year'])
        anybaseline, bins1 = retentionCurve(data[good]['latest_year'],data[good]['phd_year'])
        good = np.where((data['phd_year'] >= ymin)
                        & (data['phd_year'] <= ymax) &
                        (data['uniqueName'] == 'True') )
        test1,bins2 = retentionCurve(data[good][latest_key],data[good]['phd_year'])
        test2,bins3 = retentionCurve(data[good]['latest_year_unlinked'],data[good]['phd_year'])
        ax.plot(bins1, test1-baseline, '-', label='%i-%i' % (ymin,ymax),
                color=color)
        ax.plot(bins1, test2-baseline, '--', color=color)
        resid1 = test1-baseline
        resid2 = test2-baseline
        yerr = [[],[]]
        for r1,r2 in zip(resid1,resid2):
            min_resid = np.min([r1,r2])
            max_resid = np.max([r1,r2])
            if min_resid < 0:
                yerr[0].append(np.abs(min_resid))
            else:
                yerr[0].append(0)
            if max_resid > 0:
                yerr[1].append(max_resid)
            else:
                yerr[1].append(0)
        label = '%s-%s' % (str(ymin)[-2:],str(ymax)[-2:])
        if firstA:
            ax2.plot(bins1,baseline, color=color, label=label)
            #ax2.plot(bins1, anybaseline,'--', color=color, alpha=0.5)
            ax3.plot(bins1, anybaseline-baseline, color=color, label=label)
        else:
            ax2.errorbar(bins1,baseline, yerr=yerr, ecolor=color,
                         color=color, fmt='-o', label=label,
                         alpha=.8)


    ax.legend(numpoints=1, ncol=2)
    ax.set_xlabel('Years post PhD')
    if firstA:
        ax.set_ylabel('Active Fraction - Unique Name Active Fraction')
        figs.append(fig)
        names.append('linkCheck_1stA')
        ax3.set_ylabel('Active - Active 1st Author Fraction')
        ax3.set_xlabel('Years Post PhD')
        ax3.legend(numpoints=1, ncol=2)
        figs.append(fig3)
        names.append('staff_frac')

    else:
        ax.set_ylabel('Active Fraction - Unique Name Active Fraction')
        figs.append(fig)
        names.append('linkCheck')

    if firstA:
        ax2.legend(numpoints=1)
        ax2.set_xlim([0,17])
        ax2.set_xlabel('Years post PhD')
        ax2.set_ylabel('Fraction Still 1st Authors in ADS')
        figs.append(fig2)
        names.append('linkCheck_errorbars_1stA')
    else:
        ax2.legend(numpoints=1)
        ax2.set_xlim([0,17])
        ax2.set_xlabel('Years post PhD')
        ax2.set_ylabel('Fraction Still Active in ADS')
        figs.append(fig2)
        names.append('linkCheck_errorbars')

    return figs, names


def exampleNetworks():
    names = [u'Yoachim, P', u'Bellm, E', u'Williams, B', u'Williams, B', u'Capelo, P']
    # add some caching so it only querries once.
    if not hasattr(exampleNetworks,'results'):
        exampleNetworks.results = [None for name in names]
        exampleNetworks.graphs = [None for name in names]

    years = [2007, 2011, 2002, 2010, 2012]
    texts = ['(a)', '(b)','(c)', '(d)','(e)']
    count = 1
    figs = []
    filenames = []
    for name,year,txt in zip(names,years,texts):
        fig,ax = plt.subplots()
        figDummy, axDummy = plt.subplots()
        phdA =  list(ads.SearchQuery(q=u'bibstem:*PhDT', author=name, year=year,
                                     database='astronomy'))[-1]
        if exampleNetworks.results[count-1] is None:
            result, graph = phdArticle2row(phdA, checkUSA=False, verbose=True, returnNetwork=True)
            exampleNetworks.results[count-1] = result
            exampleNetworks.graphs[count-1] = graph
        else:
            result = exampleNetworks.results[count-1]
            graph = exampleNetworks.graphs[count-1]
        years = []
        for node in graph.nodes():
            years.append(float(node[0:4]))

        years = np.array(years)
        # Make the graph repeatable
        pos = {}
        for i, node in enumerate(graph.nodes()):
            pos[node] = (years[i],i**2)
        layout = nx.spring_layout(graph, pos=pos)
        nx.draw_networkx(graph, pos=layout, ax=ax, node_size=100,
                         node_color=years, alpha=0.5, with_labels=False)
        #nx.draw_spring(graph, ax=ax, node_size=100,
        #               node_color=years, alpha=0.5, with_labels=False)
        mappableDummy = axDummy.scatter(years,years,c=years)
        cbar = plt.colorbar(mappableDummy, ax=ax, format='%i')
        cbar.set_label('Year')
        ax.text(.1,.8, txt, fontsize=24, transform=ax.transAxes)
        ax.set_axis_off()
        figs.append(fig)
        filenames.append('example_network_%i' %count)
        count += 1
        print result
    return figs, filenames


def curvePlot(data,good, filename, title):
    # Make a handy array
    bins = np.arange(0,30,1)-0.5
    years = np.unique(data['phd_year'])
    numberActive = np.zeros((years.size,bins.size),float)
    numberPossible = np.zeros((years.size,bins.size),float)

    lastYearDist = data['latest_year'][good]-data['phd_year'][good]
    for i,year in enumerate(years):
        gg = np.where(data['phd_year'][good] == year)
        droppedHist,bins = np.histogram(lastYearDist[gg],bins)
        droppedHist = np.add.accumulate(droppedHist)
        classSize = gg[0].size
        numberActive[i][0] = classSize
        maxIndex = 2015-year
        numberActive[i][1:maxIndex+1] = classSize-droppedHist[0:maxIndex]
        numberPossible[i][0:maxIndex+1] = classSize

    # Let's bin things up by 2's
    binsize = 2
    year_mins = np.arange(1997,2011+binsize,binsize)
    year_maxes = np.arange(1998,2012+binsize,binsize)
    fig,ax = plt.subplots()
    bins = np.arange(0,30,1)-0.5

    colors = [ plt.cm.jet(x) for x in np.linspace(0, 1, year_mins.size) ]

    for ymin,ymax,color in zip(year_mins,year_maxes,colors):
        gg = np.where((years >= ymin) & (years <= ymax))
        na = numberActive[gg,:].sum(axis=1).ravel()
        npos = numberPossible[gg,:].sum(axis=1).ravel()
        good = np.where(npos > 0)
        curve = na[good]/npos[good]

        ax.plot(bins[:-1][good]+.5, curve,
                label='%i-%i (%i)' % (ymin,ymax,npos[good].max()),
                color=color)

    ax.set_xlabel('Years post PhD')
    ax.set_ylim([0.6,1])
    ax.set_ylabel('Fraction Still Active in ADS')
    ax.legend()
    ax.set_title(title)
    return [fig], [filename]


def makePlots(plot1=False, plot2=False, plot3=False, plot4=False):
    # Read in all the data
    figs = []
    names = []

    data = readYear(0, filename = 'output/all_years.dat')

    min_year = 1997
    # Make a histogram of number of PhDs per year
    good = np.where((data['noAstroJournal'] == 'None') &
                    (data['nonUS'] == 'None') &
                    (data['phd_year'] >= min_year))
    bins = np.arange(data['phd_year'][good].min()-.5, data['phd_year'][good].max()+1.5,1)

    if plot1:
        fig,ax = plt.subplots()
        blah = ax.hist(data['phd_year'][good], bins)
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of US Astro PhDs')
        figs.append(fig)
        names.append('phdsperyear')

    if plot2:
        filename = 'active_curves'
        title = 'All PhDs'
        fig,name = curvePlot(data,good, filename, title)
        figs.extend(fig)
        names.extend(name)


    if plot3:
        filename = 'active_curves_uname'
        good = np.where((data['noAstroJournal'] == 'None') &
                        (data['nonUS'] == 'None') &
                        (data['uniqueName'] == 'True') )
        title = 'Unique PhD names'
        fig,name = curvePlot(data,good, filename, title)
        figs.extend(fig)
        names.extend(name)

    # Let's plot the retention at 3,6,10 years as a function of cohort
    if plot4:
        good = np.where((data['noAstroJournal'] == 'None') &
                    (data['nonUS'] == 'None'))

        years = np.unique(data['phd_year'])
        retYears = [4,6,10]
        results=np.zeros((years.size,np.size(retYears)), dtype=float)
        lastYearDist = data['latest_year'][good]-data['phd_year'][good]
        for i,year in enumerate(years):
            inyear = np.where(data['phd_year'][good] == year)
            nInYear = np.size(inyear[0])
            for j,retYear in enumerate(retYears):
                remaining = np.size(np.where(lastYearDist[inyear] >= retYear)[0])
                results[i,j] = remaining/float(nInYear)
        fig,ax = plt.subplots()
        for i,year in enumerate(retYears):
            ack = np.where(results[:,i] != 0)[0][:-1]
            blah = ax.plot(years[ack],results[ack,i], label='%i years' % year)
        ax.set_xlabel('PhD Cohort Year')
        ax.set_ylabel('Fraction Active')
        ax.legend(loc='upper right')
        figs.append(fig)
        names.append('retention_by_class')
        return figs, names

if __name__ == '__main__':

    parser = arg.ArgumentParser(description="")

    parser.add_argument('--plot1', dest='plot1', action='store_true')
    parser.add_argument('--plot2', dest='plot2', action='store_true')
    parser.add_argument('--plot3', dest='plot3', action='store_true')
    parser.add_argument('--plot4', dest='plot4', action='store_true')
    parser.add_argument('--network', dest='network', action='store_true')
    parser.add_argument('--linkCheck', dest='linkCheck', action='store_true')
    parser.add_argument('--all', dest='all', action='store_true')

    parser.set_defaults(plot1=False,plot2=False,plot3=False,
                        plot4=False, network=False, linkCheck=False)

    args = parser.parse_args()
    darg = vars(args)
    if args.all:
        for key in darg.keys():
            darg[key] = True

    passed_kwargs = dict(plot1=args.plot1,
              plot2=args.plot2,
              plot3=args.plot3,
              plot4=args.plot4)

    funcs = []
    kwargs = []
    if True in passed_kwargs.values():
        funcs.append(makePlots)
        kwargs.append(passed_kwargs)

    if args.network:
        funcs.append(exampleNetworks)
        kwargs.append({})

    if args.linkCheck:
         funcs.append(linkCheck)
         kwargs.append({})
         funcs.append(linkCheck)
         kwargs.append({'firstA':True})


    spp.plot_multi_format(funcs, plot_kwargs=kwargs,
                          usetex=False, outdir='../plots')
