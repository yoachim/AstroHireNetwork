#!/usr/bin/env python
import numpy as np
from runYear import readYear
import glob
import matplotlib.pylab as plt
import argparse as arg
import networkx as nx
import ads
from grabPhdClass import phdArticle2row



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


def linkCheck():
    """
    Check to see if we are over or under-linking papers using the
    unique name flag
    """
    data = readYear(0, filename = 'output/all_years.dat')
    # Make a histogram of number of PhDs per year
    good = np.where((data['noAstroJournal'] == 'None') &
                    (data['nonUS'] == 'None'))

    data = data[good]

    binsize = 2
    year_mins = np.arange(1999,2011+binsize,binsize)
    year_maxes = np.arange(2000,2012+binsize,binsize)
    fig,ax = plt.subplots()

    colors = [ plt.cm.jet(x) for x in np.linspace(0, 1, year_mins.size) ]

    for ymin,ymax,color in zip(year_mins,year_maxes,colors):
        good = np.where((data['phd_year'] >= ymin)
                        & (data['phd_year'] <= ymax))

        baseline, bins1 = retentionCurve(data[good]['latest_year'],data[good]['phd_year'])
        good = np.where((data['phd_year'] >= ymin)
                        & (data['phd_year'] <= ymax) &
                        (data['uniqueName'] == 'True') )
        test1,bins2 = retentionCurve(data[good]['latest_year'],data[good]['phd_year'])
        test2,bins3 = retentionCurve(data[good]['latest_year_unlinked'],data[good]['phd_year'])
        ax.plot(bins1, test1-baseline, '-', label='%i-%i' % (ymin,ymax),
                color=color)
        ax.plot(bins1, test2-baseline, '--', color=color)


    ax.legend()
    ax.set_xlabel('Years post PhD')
    ax.set_ylabel('Active Fraction - Unique Name Active Fraction')
    fig.savefig('../plots/linkCheck.pdf')
    plt.close(fig)



def exampleNetworks():
    names = ['Yoachim, P', 'Bellm, E', 'Williams, B', 'Williams, B' ]
    years = [2007, 2011, 2002, 2010]
    count = 1
    for name,year in zip(names,years):
        phdA =  list(ads.query('bibstem:*PhDT', authors=name, dates=year,
                               database='astronomy', rows='all'))

        result,graph = phdArticle2row(phdA[0], checkUSA=False, verbose=True, returnNetwork=True)
        nx.draw_spring(graph)
        plt.savefig('../plots/example_network_%i.pdf' %count )
        count += 1
        plt.close('all')
        print result


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
    year_mins = np.arange(1999,2011+binsize,binsize)
    year_maxes = np.arange(2000,2012+binsize,binsize)
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
    fig.savefig(filename)
    plt.close(fig)


def makePlots(plot1=False, plot2=False, plot3=False, plot4=False):
    # Read in all the data
    data = readYear(0, filename = 'output/all_years.dat')

    # Make a histogram of number of PhDs per year
    good = np.where((data['noAstroJournal'] == 'None') &
                    (data['nonUS'] == 'None'))
    bins = np.arange(data['phd_year'][good].min()-.5, data['phd_year'][good].max()+1.5,1)

    if plot1:
        fig,ax = plt.subplots()
        blah = ax.hist(data['phd_year'][good], bins)
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of US Astro PhDs')
        fig.savefig('../plots/phdsperyear.pdf')
        plt.close(fig)

    if plot2:
        filename = '../plots/active_curves.pdf'
        title = 'All PhDs'
        curvePlot(data,good, filename, title)
    if plot3:
        filename = '../plots/active_curves_uname.pdf'
        good = np.where((data['noAstroJournal'] == 'None') &
                        (data['nonUS'] == 'None') &
                        (data['uniqueName'] == 'True') )
        title = 'Unique PhD names'
        curvePlot(data,good, filename, title)

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
        fig.savefig('../plots/retention_by_class.pdf')
        plt.close(fig)

if __name__ == '__main__':

    parser = arg.ArgumentParser(description="")

    parser.add_argument('--plot1', dest='plot1', action='store_true')
    parser.add_argument('--plot2', dest='plot2', action='store_true')
    parser.add_argument('--plot3', dest='plot3', action='store_true')
    parser.add_argument('--plot4', dest='plot4', action='store_true')
    parser.add_argument('--network', dest='network', action='store_true')
    parser.add_argument('--linkCheck', dest='linkCheck', action='store_true')


    parser.set_defaults(plot1=False,plot2=False,plot3=False,
                        plot4=False, network=False, linkCheck=False)

    args = parser.parse_args()

    makePlots(plot1=args.plot1,
              plot2=args.plot2,
              plot3=args.plot3,
              plot4=args.plot4)

    if args.network:
        exampleNetworks()

    if args.linkCheck:
         linkCheck()
