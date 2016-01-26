import numpy as np
from runYear import readYear
from grabPhdClass import *


data = readYear(0, filename = 'output/all_years.dat')

good = np.where((data['noAstroJournal'] == 'None') &
                (data['nonUS'] == 'None') & (data['uniqueName'] == 'True')
                & (data['phd_year'] > 2009)
                & (data['latest_year_unlinked'] > data['latest_year']))
data = data[good]
