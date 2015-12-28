from grabPhdClass import grabPhdClass

# Do a few years and pull out the affiliations

tryYears = [1990, 1995, 2000, 2005, 2010]

instList = []

for year in tryYears:
    print 'grabbing year %i' % year
    phds = grabPhdClass(year)
    for phd in phds:
        instList.append(phd.aff[0])

instList = list(set(instList))

f = open('allInst.dat','w')
for inst in instList:
    print >>f, inst.encode('utf-8')

f.close()
