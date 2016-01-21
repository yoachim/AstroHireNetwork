import numpy as np
from runYear import readYear
import glob
import matplotlib.pylab as plt


# Read in all the data
data = readYear(0, filename = 'output/all_years.dat')

# Make a histogram of number of PhDs per year
good = np.where((data['noAstroJournal'] == 'None') &
                (data['nonUS'] == 'None'))
bins = np.arange(data['phd_year'][good].min()-.5, data['phd_year'][good].max()+1.5,1)
fig,ax = plt.subplots()
blah = ax.hist(data['phd_year'][good], bins)
ax.set_xlabel('Year')
ax.set_ylabel('Number of US Astro PhDs')
fig.savefig('../plots/phdsperyear.pdf')
plt.close(fig)


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


# OK, so I need for each integer year, the number of possible people still active, and the actual number still active

colors = [ plt.cm.jet(x) for x in np.linspace(0, 1, year_mins.size) ]

for ymin,ymax,color in zip(year_mins,year_maxes,colors):
    gg = np.where((years >= ymin) & (years <= ymax))
    na = numberActive[gg,:].sum(axis=1).ravel()
    npos = numberPossible[gg,:].sum(axis=1).ravel()
    good = np.where(npos > 0)
    curve = na[good]/npos[good]

    ax.plot(bins[:-1][good]+.5, curve,
            label='%i-%i' % (ymin,ymax), color=color)

ax.set_xlabel('Years post PhD')
ax.set_ylabel('Fraction Still Active in ADS')
ax.legend()
ax.set_title('Astronomy PhD Retention')

fig.savefig('../plots/active_curves.pdf')

# Next up.
# 1) Bin into multiple years.
# 2) Check unique names only
# 3) Maybe do a test that looks at fraction of people who end up in forign institutions.
