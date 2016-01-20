import numpy as np
from runYear import readYear
import glob
import matplotlib.pylab as plt

files = glob.glob('output/*.dat')
years = [int(filename[-8:-4]) for filename in files]

bins = np.arange(0,30,1)-0.5

years = [1999,2000,2001, 2009,2010, 2011, 2012]
#years = [1995,1996,1997,1998]
first = True
for year in years:
    data = readYear(year)
    good = np.where( (data['noAstroJournal'] != 'True') & (data['nonUS'] != 'True'))

    print '%i: %i' % (year, np.size(good[0]))
    nDiss = good[0].size

    yearDist = np.sort(data['latest_year'][good]-year)+1
    droppedHist,bins = np.histogram(yearDist,bins)
    stillActive = nDiss-np.add.accumulate(droppedHist)

    good = np.where(stillActive > 0)

    if first:
        label = 'PhD year = %i' % year
        first = False
    else:
        label = year

    # add the [:-1] to crop off 2016.
    plt.plot(bins[:-1][good][:-1]+.5, stillActive[good][:-1]/float(nDiss), label=label)

plt.xlabel('Years post PhD')
plt.ylabel('Fraction Still Active in ADS')
plt.legend()
plt.title('Astronomy PhD Retention')



# Next up.
# 1) Bin into multiple years.
# 2) Check unique names only
# 3) Maybe do a test that looks at fraction of people who end up in forign institutions.
