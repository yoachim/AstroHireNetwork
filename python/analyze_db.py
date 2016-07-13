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
        print 'Total USA Astro PhDs w/ unique names = %i' % len(self.astro_df[self.astro_df.uniqueName == True])

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

        still_active = np.sum(still_active, axis=0)
        raw_active = np.sum(raw_active, axis=0)
        hist_norm = np.sum(hist_norm,axis=0) * np.max(still_active)

        return still_active, raw_active, hist_norm

    def _h2cm(self, linked_hist, years, bins, truncate_year=2015):
        """
        Run the above for each year and combine
        """
        still_active = 0
        raw_active = 0
        hist_norm = 0
        for year in np.unique(years):
            oneYear = np.where(years == year)[0]
            sa, ra, hn = self._hist2curve(linked_hist[oneYear, :], [year], bins, truncate_year=truncate_year)
            mask = np.where(hn == 0)
            sa[mask] = 0
            ra[mask] = 0
            still_active += sa
            raw_active += ra
            hist_norm += hn
        still_active = still_active/hist_norm
        raw_active = raw_active/hist_norm
        return still_active, raw_active

    def plot_retention_curve(self, first_author=False):
        """
        return the retention curves as figures.
        """

        years_pre_phd = 7
        year_bins = np.arange(28)-years_pre_phd-0.5
        bins = year_bins[:-1]+.5

        fig, ax = plt.subplots()
        fig2, ax2 = plt.subplots()
        fig3, ax3 = plt.subplots()
        fig_fa, ax_fa = plt.subplots()

        fig_raw1, ax_raw1 = plt.subplots()

        # ok, a final figure with error bars
        fig_eb, ax_eb = plt.subplots()

        year_mins = np.arange(1998, 2012+2, 2)
        year_maxes = np.arange(1999, 2013+2, 2)
        #year_mins = np.arange(2006,2014,1)
        #year_maxes = np.arange(2006,2014,1)
        colors = [plt.cm.jet(x) for x in np.linspace(0, 1, year_mins.size)]


        # Can use all_hist as well, fa_hist, fa_linked_hist

        for year_min, year_max, color in zip(year_mins, year_maxes, colors):
            curveDict_active = {}
            curveDict_raw = {}
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
            years_un = self.astro_df[condition_un]['phd_year'].values

            # Convert to curves. The raw_active curves show what it would look like with no
            # knowledge of future publications
            still_active, raw_active = self._h2cm(linked_hist, years, bins)
            still_active_unique, raw_active_unique = self._h2cm(linked_hist_un, years_un, bins)

            still_active_fa, raw_active_fa = self._h2cm(linked_fa_hist, years, bins)
            sa_fa_u, raw_sa_fa_u = self._h2cm(linked_fa_hist_un, years_un, bins)
            sa_fa_u_un, blah = self._h2cm(fa_hist_un, years_un, bins)
            # OK, now I want the plain fa_hist ones, to check for under-linking.

            # XXX--maybe dump these into a dictionary for easier sorting and generating error bars?

            # XXX--need to make error bars go in 2 directions. Use the
            # Unique names as another test.
            yerr = still_active-raw_active
            #ax.errorbar(bins, still_active, yerr=yerr, color=color, fmt='-o',
            #            ecolor=color, label=label)
            ax.plot(bins, still_active, '-o', color=color, label=label)
            ax2.plot(bins, still_active_unique, '-o', color=color, label=label)

            ax_fa.plot(bins, still_active_fa, '-o', color=color,
                       label=label)
            ax3.plot(bins, sa_fa_u, '-o', color=color,
                       label=label)
            ax_raw1.plot(bins, raw_sa_fa_u, '-o', color=color,
                       label=label)

            # Should be linked 1st author, linked 1st author with unique names, and 1st author unique name (not linked)
            rel_curves = np.array([still_active_fa, sa_fa_u, sa_fa_u_un])
            lower_bars = np.abs(np.min(rel_curves, axis=0) - still_active_fa)
            upper_bars = np.abs(np.max(rel_curves, axis=0) - still_active_fa)
            ax_eb.errorbar(bins, still_active_fa, fmt='-o', yerr=[lower_bars, upper_bars],
                           ecolor=color,  color=color, label=label)
            ax_eb.set_title('US Astronomy PhDs')


        ax.set_xlim([0, 20])
        ax.set_ylim([0.2, 1])
        ax.legend(numpoints=1, ncol=2)
        ax.set_xlabel('Years post PhD')
        ax.set_ylabel('Fraction Still Active on ADS')

        ax2.set_xlim([0, 20])
        ax2.set_ylim([0.2, 1])
        ax2.legend(numpoints=1, ncol=2)
        ax2.set_xlabel('Years post PhD')
        ax2.set_ylabel('Fraction Still Active on ADS (unique names)')

        ax_fa.set_xlim([0, 20])
        ax_fa.set_ylim([0, 1])
        ax_fa.legend(numpoints=1, ncol=2)
        ax_fa.set_xlabel('Years post PhD')
        ax_fa.set_ylabel('Fraction Still 1st Authors')

        ax3.set_xlim([0, 20])
        ax3.set_ylim([0, 1])
        ax3.legend(numpoints=1, ncol=2)
        ax3.set_xlabel('Years post PhD')
        ax3.set_ylabel('Fraction Still 1st Authors (unique names)')

        ax_raw1.set_xlim([0, 20])
        ax_raw1.set_ylim([0, 1])
        ax_raw1.legend(numpoints=1, ncol=2)
        ax_raw1.set_xlabel('Years post PhD')
        ax_raw1.set_ylabel('Fraction Still 1st Authors')
        ax_raw1.set_title('Real Time')

        ax_eb.set_xlim([0, 20])
        ax_eb.set_ylim([0.2, 1])
        ax_eb.legend(numpoints=1, ncol=2)
        ax_eb.set_xlabel('Years post PhD')
        ax_eb.set_ylabel('Fraction Still 1st Authors')
        ax_eb.set_title('')

        return [fig, fig_fa, fig2,
                fig3, fig_raw1, fig_eb], ['rc', 'rc_fa', 'rc_unique',
                                          'rc_fa_unique', 'rc_fa_raw', 'rc_eb']


if __name__ == '__main__':

    # Read in the dataframe generated by generate_db.py
    ack = phd_db()
    ack.print_stats()

    plot_funcs = []
    kwargs = []

    plot_funcs.append(ack.plot_phds_per_year)
    kwargs.append({})

    plot_funcs.append(plot_example_networks)
    kwargs.append({})

    plot_funcs.append(ack. plot_retention_curve)
    kwargs.append({})


    # Wow, I am getting a much better looking histogram of
    # number of astro phds per year than before.  Need to spot check
    # some of the 2008 ones to see if they are real.

    # --Looks like the new ones are just better? Maybe change the AAS checking since that can pull in planetary people?

    spp.plot_multi_format(plot_funcs, plot_kwargs=kwargs,
                          usetex=False, outdir='../new_plots')
