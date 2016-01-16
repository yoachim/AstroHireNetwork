import numpy as np
from runYear import readYear
import glob
import matplotlib.pylab as plt

files = glob.glob('output/*.dat')
years = [int(filename[-8:-4]) for filename in files]

bins = np.arange(0,30,1)-0.5

for year in years:
    data = readYear(year)
    good = np.where( (data['noAstroJournal'] != 'True') & (data['nonUS'] != 'True'))

    nDiss = good[0].size

    yearDist = np.sort(data['latest_year'][good]-year)
    droppedHist,bins = np.histogram(yearDist,bins)
    stillActive = nDiss-np.add.accumulate(droppedHist)

    plt.plot(bins[:-1]+.5, stillActive/float(nDiss), label=year)

plt.xlabel('Years post PhD')
plt.ylabel('Fraction still active')
plt.legend()