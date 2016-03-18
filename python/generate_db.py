#! /usr/bin/env python
import numpy as np
import glob
from utils import paper_network, authSimple, inAstroJ
import os

# Let's read in the save files, generate the author network, and record the analysis of it


def load_papers(filename):
    temp = np.load(filename)
    papers = temp['result'][()].copy()
    flags = temp['flags'][()].copy()
    temp.close()
    return papers, flags

if __name__ == '__main__':

    # Set the years we want to restore and analyze
    years = [2007]
    # Create a dict of lists so that it's easy to convert to pandas later
    all_results = {'phd_year':[], 'nonUS':[], 'phd_bibcode':[], 'author':[],
                   'astroPublication':[], 'last_year':[], 'last_1st_year':[],
                   'first_author_year_dist':[], 'uniqueName':[]}
    years_pre_phd = 7

    year_bins = np.arange(30)-years_pre_phd-0.5
    for year in years:
        all_results['phd_year'].append(year)
        filenames = glob.glob(os.path.join('output',str(year),'*PhDT*.npz'))
        for filename in filenames:
            phd_bibcode = os.path.basename(filename).replace('.npz','').replace('_','.')
            all_results['phd_bibcode'].append(phd_bibcode)
            papers, flags = load_papers(filename)
            phd = [paper for paper in papers if phd_bibcode in paper['bibcode']][0]
            all_results['author'].append(phd['author'][0])
            connected_papers = None
            network = None
            fa_hist = None
            flags['astroPublication'] = None
            last_year = None
            last_1st_year = None
            fa_hist = None
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
                    first_author_papers =[paper for paper in connected_papers if
                                          authSimple(phd['author'][0]) == authSimple(paper['first_author'] )]
                    fap_years = [int(paper['year']) for paper in first_author_papers]
                    last_1st_year = np.max(fap_years)
                    last_year = np.max([int(paper['year']) for paper in connected_papers])
                    fa_hist, bins = np.histogram(np.array(fap_years)-phd['year'], bins=year_bins)
                    clip = np.where(fa_hist > 0)[0].max()
                    fa_hist = fa_hist[0:clip+1]
                    # Check for Astro again
                    if not inAstroJ(connected_papers):
                        flags['astroPublication'] = False
                    else:
                        flags['astroPublication'] = True
            # OK, here's where I format the results
            all_results['nonUS'].append(flags['nonUS'])
            all_results['astroPublication'].append(flags['astroPublication'])
            all_results['last_year'].append(last_year)
            all_results['last_1st_year'].append(last_1st_year)
            all_results['first_author_year_dist'].append(fa_hist)
            all_results['uniqueName'].append(flags['uniqueName'])

    # Convert the results to a dataframe and save it
