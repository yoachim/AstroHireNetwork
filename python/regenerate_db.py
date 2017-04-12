#! /usr/bin/env python
import numpy as np
import glob
from utils import paper_network, authSimple, inAstroJ
import os
import pandas as pd
import sys
from grabPhdClass import phdArticle2row
import ads
from time import sleep


# Let's add on the h-index calculation for the known astonomers

def restore_db():
    filenames = glob.glob('phd_store*.h5')
    data_df = pd.read_hdf(filenames[0], 'author_df')
    for filename in filenames[1:]:
        temp = pd.read_hdf(filename, 'author_df')
        data_df = data_df.append(temp, ignore_index=True)

    # make a dataframe that is just US astro PhDs
    astro_df = data_df[(data_df['nonUS'] == False) &
                       (data_df['astroPublication'] == True)]
    return astro_df, data_df


astro_df, data_df = restore_db()

years = np.arange(1997, 2014)
for year in years:
    new_rows = {}
    keys = phdArticle2row(None, justKeys=True)
    for key in keys:
        new_rows[key] = []

    for j, bibcode in enumerate(astro_df.loc[astro_df['phd_year'] == year]['phd_bibcode']):
        for i in range(4):
            try:
                phdA = list(ads.SearchQuery(bibcode=bibcode))
                row = phdArticle2row(phdA[0])
                for key in keys:
                    new_rows[key].append(row[key])
                print year, j, row['hindex']
            except:
                sleep(5)
            else:
                break
    new_frame = pd.DataFrame(new_rows, columns=new_rows.keys())
    new_frame.to_hdf('with_hindex_%i.h5' % year, 'author_df')

