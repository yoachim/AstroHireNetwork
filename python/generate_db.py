#! /usr/bin/env python
import numpy as np
import glob
from utils import paper_network, authSimple, inAstroJ
import os
import pandas as pd
import sys

# Let's read in the save files, generate the author network, and record the analysis of it


def load_papers(filename):
    temp = np.load(filename)
    papers = temp['result'][()].copy()
    flags = temp['flags'][()].copy()
    temp.close()
    return papers, flags

if __name__ == '__main__':

    # Set the years we want to restore and analyze
    #years = range(1997,2014)
    years = range(1999, 2014)
    # Create a dict of lists so that it's easy to convert to pandas later

    keys = {'phd_year', 'nonUS', 'astroPublication', 'phd_bibcode', 'author',
            'last_year', 'last_1st_year',
            'uniqueName','fa_hist', 'fa_linked_hist',
            'linked_hist', 'all_hist'}
    hist_keys = []
    all_results = {}
    for key in keys:
        all_results[key] = []

    years_pre_phd = 7

    year_bins = np.arange(28)-years_pre_phd-0.5
    for year in years:
        print 'year = %i' % year
        filenames = glob.glob(os.path.join('output',str(year),'*PhDT*.npz'))
        maxI = len(filenames)
        for i,filename in enumerate(filenames):

            # Progress Bar
            progress = i/float(maxI)*100
            text = "\rprogress = %.1f%%"%progress
            sys.stdout.write(text)
            sys.stdout.flush()

            phd_bibcode = os.path.basename(filename).replace('.npz','').replace('_','.')
            all_results['phd_bibcode'].append(phd_bibcode)
            papers, flags = load_papers(filename)
            phd = [paper for paper in papers if phd_bibcode in paper['bibcode']][0]
            all_results['author'].append(phd['author'][0])
            connected_papers = None
            network = None
            flags['astroPublication'] = None
            last_year = None
            last_1st_year = None
            fa_hist = np.array([], dtype=int) #year_bins[1:]*0
            all_hist = np.array([], dtype=int) #year_bins[1:]*0
            fa_linked_hist = np.array([], dtype=int) #year_bins[1:]*0
            linked_hist = np.array([], dtype=int) #year_bins[1:]*0
            unique_name = None
            flagKeys = ['astroPublication', 'nonUS', 'uniqueName']
            for key in flagKeys:
                if key not in flags.keys():
                    flags[key] = None

            if not flags['nonUS']:
                # Check for Astro pub in list
                if not inAstroJ(papers):
                    flags['astroPublication'] = False
                else:
                    connected_papers, network = paper_network(papers, phd, authSimple(phd['author'][0]))
                    first_author_linked_papers =[paper for paper in connected_papers if
                                                    authSimple(phd['author'][0]) ==
                                                    authSimple(paper['first_author'] )]
                    first_author_papers = [paper for paper in papers if
                                           authSimple(phd['author'][0]) ==
                                           authSimple(paper['first_author'] )]

                    fap_years = [int(paper['year']) for paper in first_author_papers]
                    linked_years = [int(paper['year']) for paper in connected_papers]
                    linked_fap_years = [int(paper['year']) for paper in first_author_linked_papers]
                    all_years = [int(paper['year']) for paper in papers]

                    last_1st_year = np.max(fap_years)
                    last_year = np.max([int(paper['year']) for paper in connected_papers])

                    fa_hist, bins = np.histogram(np.array(fap_years)-int(phd['year']), bins=year_bins)
                    fa_linked_hist, bins = np.histogram(np.array(linked_fap_years)-int(phd['year']),
                                                        bins=year_bins)
                    linked_hist, bins = np.histogram(np.array(linked_years)-int(phd['year']), bins=year_bins)
                    all_hist, bins = np.histogram(np.array(all_years)-int(phd['year']), bins=year_bins)
                    # Check for Astro again
                    if not inAstroJ(connected_papers):
                        flags['astroPublication'] = False
                    else:
                        flags['astroPublication'] = True
            # Append the rest of the results
            all_results['nonUS'].append(flags['nonUS'])
            all_results['astroPublication'].append(flags['astroPublication'])
            all_results['last_year'].append(last_year)
            all_results['last_1st_year'].append(last_1st_year)
            all_results['uniqueName'].append(flags['uniqueName'])
            all_results['fa_hist'].append(fa_hist.tolist())
            all_results['fa_linked_hist'].append(fa_linked_hist.tolist())
            all_results['all_hist'].append(all_hist.tolist())
            all_results['linked_hist'].append(linked_hist.tolist())
            all_results['phd_year'].append(year)

        # Convert the results to a dataframe and save it
        author_df = pd.DataFrame(all_results, columns=all_results.keys())
        author_df.to_hdf('phd_store_%i.h5' % year, 'author_df')
        #store.append('author_df', author_df)
        # Clear out some memory:
        for key in keys:
            all_results[key] = []
