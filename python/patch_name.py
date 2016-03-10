from grabPhdClass import grabPhdClass, checkUSAff, authorsPapers, authSimple
import os,argparse
import numpy as np
import glob
import datetime
import ads


# Do a quick patch to add the unique name flag
outDir = 'output/%s' % 2007
fileList = glob.glob(os.path.join(outDir, '*.npz'))

for i,filename in enumerate(fileList[354:]):
    print i
    temp = np.load(filename)
    result = temp['result'][()].copy()
    flags = temp['flags'][()].copy()
    temp.close()

    if flags['nonUS']:
        phd_indx = [i for i,article in enumerate(result) if 'PhDT' in article['bibcode']]
        phd = result[phd_indx[0]]
        ack = list(ads.SearchQuery(q='bibstem:"*PhDT" author:"%s"' % authSimple(phd['author'][0].encode('utf-8')),
                                   database='astronomy'))
        if len(ack) > 1:
            titles = set([paper.title[0].lower() for paper in ack if paper.title is not None])
            if len(titles) > 1:
                flags['uniqueName'] = False
            else:
                flags['uniqueName'] = True
        else:
            flags['uniqueName'] = True

        savefile = filename
        np.savez(savefile, result=result, flags=flags)
