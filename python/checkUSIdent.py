import numpy as np
from grabPhdClass import checkUSAff




# check that the names in simpleUSList.dat correctly identify US institutions

allusInst = np.genfromtxt('usInst.dat', dtype='|S50', delimiter='$$', comments='#')

results = [checkUSAff(aff) for aff in allusInst]
