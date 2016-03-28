import numpy as np
import matplotlib.pylab as plt
import pandas as pd
import glob
import sys
# Try out my tool to output pub-ready and slide-ready at same time
sys.path.append("/Users/yoachim/gitRepos/matplotlib_pubplots/python")
import set_plot_params as spp
from make_plots import plot_example_networks

class phd_db(object):
    """
    Class to read in saved pandas data frames and then generate useful plots.
    """

    def __init__(self):

        filenames = glob.glob('phd_store*.h5')
        self.data_df = pd.read_hdf(filenames[0], 'author_df')
        for filename in filenames[1:]:
            temp = pd.read_hdf(filename, 'author_df')
            self.data_df =  self.data_df.append(temp, ignore_index=True)

        # make a dataframe that is just US astro PhDs
        self.astro_df = self.data_df[(self.data_df['nonUS'] == False) &
                                     (self.data_df['astroPublication'] == True)]
    def print_stats(self):
        """
        Print some basic stats about the papers
        """
        print 'Total number of PhDs found = %i' % len(self.data_df.index)
        print 'Total USA Astro PhDs found = %i' % len(self.astro_df.index)

    def plot_phds_per_year(self):
        """
        Return a matplotlib figure and base filename.
        """
        fig,ax = plt.subplots()
        years = self.astro_df['phd_year'].values
        bins = np.arange(years.min(), years.max()+2, 1) - 0.5
        blah = ax.hist(years, bins)
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of US Astro PhDs')

        return [fig], ['phdsperyear']


    def _hist2curve(self, linked_hist, years, bins, truncate_year=2015):
        """
        Take the 2-d array that is number of papers/year and each row is a different astronomer
        """

        nPhD = linked_hist.shape[0]
        # Curve that accounts for sometimes it appears an author has
        # left the field, but they actually will publish again later
        nz = np.where(linked_hist != 0)
        raw_active = linked_hist*0
        raw_active[nz] += 1
        # Curve where we know the future
        still_active = np.add.accumulate(linked_hist[:,::-1], axis=1)[:,::-1]
        still_active[np.where(still_active > 0)] = 1

        # Calculate total number of potential authors in a given year bin.
        hist_norm = still_active*0.
        for year in np.unique(years):
            oneYear = np.where(years == year)[0]
            hist_norm[oneYear,:] += 1
            yb = bins+year
            left_limit = np.where(yb > truncate_year)[0].min()
            hist_norm[oneYear,left_limit:] = 0

            #still_active[oneYear,left_limit:] = 0
            #raw_active[oneYear,left_limit:] = 0


        hist_norm = np.sum(hist_norm,axis=0)
        still_active = np.sum(still_active, axis=0)/hist_norm
        raw_active = np.sum(raw_active, axis=0)/hist_norm

        return still_active, raw_active

    def plot_retention_curve(self, first_author=False):
        """
        return the retention curves as figures.
        """

        years_pre_phd = 7
        year_bins = np.arange(28)-years_pre_phd-0.5
        bins = year_bins[:-1]+.5

        fig,ax = plt.subplots()

        fig_fa, ax_fa = plt.subplots()

        #year_mins = np.arange(1999,2011+2,2)
        #year_maxes = np.arange(2000,2012+2,2)
        year_mins = np.arange(2006,2014,1)
        year_maxes = np.arange(2006,2014,1)
        colors = [ plt.cm.jet(x) for x in np.linspace(0, 1, year_mins.size) ]


        # Can use all_hist as well, fa_hist, fa_linked_hist

        for year_min, year_max, color in zip(year_mins, year_maxes, colors):
            label = str(year_min)[-2:]+'-'+str(year_max)[-2:]
            # in the year range
            condition = (self.astro_df.phd_year >= year_min) & (self.astro_df.phd_year <= year_max)
            # In the year range, and a unique name
            condition_un = (self.astro_df.phd_year >= year_min) & (self.astro_df.phd_year <= year_max) & (self.astro_df.uniqueName)
            # need to convert "array-of-lists" to 2D array.
            # Any entries, and any entries for the unique name subset
            linked_hist = np.array(self.astro_df[condition]['linked_hist'].values.tolist())
            linked_hist_un = np.array(self.astro_df[condition_un]['linked_hist'].values.tolist())

            #
            fa_hist = np.array(self.astro_df[condition]['fa_hist'].values.tolist())
            fa_hist_un = np.array(self.astro_df[condition_un]['fa_hist'].values.tolist())
            linked_fa_hist = np.array(self.astro_df[condition]['fa_linked_hist'].values.tolist())
            linked_fa_hist_un = np.array(self.astro_df[condition_un]['fa_linked_hist'].values.tolist())

            years = self.astro_df[condition]['phd_year'].values

            # Convert to curves
            still_active, raw_active = self._hist2curve(linked_hist, years, bins)

            still_active_fa, raw_active_fa = self._hist2curve(linked_fa_hist, years, bins)

            # XXX--need to make error bars go in 2 directions. Use the
            # Unique names as another test.
            yerr = still_active-raw_active
            ax.errorbar(bins, still_active, yerr=yerr, color=color, fmt='-o',
                        ecolor=color, label=label)

            ax_fa.plot(bins, still_active_fa, '-o', color=color,
                       label=label)


        ax.set_xlim([0,20])
        ax.set_ylim([0.2,1])
        ax.legend(numpoints=1, ncol=2)
        ax.set_xlabel('Years post PhD')
        ax.set_ylabel('Fraction Still Active on ADS')


        ax_fa.set_xlim([0,20])
        ax_fa.set_ylim([0,1])
        ax_fa.legend(numpoints=1, ncol=2)
        ax_fa.set_xlabel('Years post PhD')
        ax_fa.set_ylabel('Fraction Still 1st Authors')


        return [fig, fig_fa], ['retention_curve', 'retention_curve_fa']


if __name__ == '__main__':

    # Read in the dataframe generated by generate_db.py
    ack = phd_db()
    ack.print_stats()

    plot_funcs = []
    kwargs = []

    #plot_funcs.append(ack.plot_phds_per_year)
    #kwargs.append({})

    #plot_funcs.append(plot_example_networks)
    #kwargs.append({})

    plot_funcs.append(ack. plot_retention_curve)
    kwargs.append({})


    # Wow, I am getting a much better looking histogram of
    # number of astro phds per year than before.  Need to spot check
    # some of the 2008 ones to see if they are real.

    # --Looks like the new ones are just better? Maybe change the AAS checking since that can pull in planetary people?

    spp.plot_multi_format(plot_funcs, plot_kwargs=kwargs,
                          usetex=False, outdir='../new_plots')
