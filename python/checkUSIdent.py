import numpy as np
from grabPhdClass import checkUSAff




# check that the names in simpleUSList.dat correctly identify US institutions

allusInst = np.genfromtxt('usInst.dat', dtype='|S100', delimiter='$$', comments='#')

results = np.array([checkUSAff(aff) for aff in allusInst])

print 'US institions which did not pass the test that should have'
print allusInst[np.where(results == False)]
print '--------'

allInst = np.genfromtxt('allInst.dat', dtype='|S100', delimiter='$$', comments='#')

forignInst = np.array([inst for inst in allInst if inst not in allusInst])
results = np.array([checkUSAff(aff) for aff in forignInst])
print 'non-US institutions that passed the test that should not have'
print forignInst[np.where(results == True)]
print '--------'
