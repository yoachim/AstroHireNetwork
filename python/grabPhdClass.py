import numpy as np
import ads

# Get the authors, institutions for a given dissertation year

# looks like I should try using https://github.com/andycasey/ads
# to get things going.

year = 1997

#papers = ads.query("supernova", sort="citations", rows=5)

#papers = ads.query('United States', start_year=year, end_year=year, ref_stems='PhDT', database='astronomy')
# can add rows = 'all' to get it all.


# This works to search by bibcode:  bybibcode = list(ads.query('bibcode:2015AAS...22533641Y'))


# OK, now how do I get all of them?--boom, rows='all'
# ack = list(ads.query('bibstem:*PhDT', dates='1997', database='astronomy', rows='all'))

# with that, maybe write out:  year, author[0], affiliation, bibcode
# Then I can make my affil dict
