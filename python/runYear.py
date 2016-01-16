#! /usr/bin/env python
from grabPhdClass import grabPhdClass, phdArticle2row
import os,argparse
import numpy as np

def readYear(year, filename=None):
    """
    Read in the data for a given year
    """
    if filename is None:
        filename = 'output/%i.dat' %year
    keys = phdArticle2row(None, justKeys=True)
    st='|S50'
    types = [st,int,st,st,int,st,int,st,int,int,int,st,st]
    data = np.genfromtxt(filename, delimiter=';; ', skip_header=1,
                         dtype=zip(keys,types))

    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a database of astro phds for a given year")
    parser.add_argument("year", type=int, help="year to query")

    args = parser.parse_args()

    outDir = 'output'
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    filename = os.path.join(outDir,str(args.year)+'.dat')
    resultKeys = phdArticle2row(None, justKeys=True)
    if os.path.isfile(filename):
        print 'restoring results already made for this year'
        alreadyDone =  readYear(args.year, filename=filename)
        doneBibcodes = alreadyDone['phd_bibcode'].tolist()
        print 'restored %i records for this year' % len(doneBibcodes)
        f = open(filename, 'a')
    else:
        doneBibcodes = []
        f = open(filename,'w' )
        header = ''
        for key in resultKeys:
            header += '; %s' % key
            header = header[2:]

        print >>f, header

    print 'Querying for year %i' % args.year
    phdArticles = grabPhdClass(args.year)
    print 'Found %i articles' % len(phdArticles)

    phdArticles = [article for article in phdArticles if article.bibcode not in doneBibcodes]
    print 'Removed already run bibcodes and have %i left' % len(phdArticles)

    for phd in phdArticles:
        if hasattr(phd,'year'):
            print 'Generating row for:', phd
            row = phdArticle2row(phd, verbose=True)
            row.replace('#','') #  Strip out unintended comment symbols
            out = u''
            for key in resultKeys:
                if (type(row[key]) == str) | (type(row[key]) == type(u'unicode')):
                    temp = row[key].encode('utf-8')
                else:
                    temp = str(row[key])
                try:
                    out += temp+';; '
                except:
                    out += 'garblegarblestring ;; '
            out = out[:-3]
            print >>f, out

    f.close()
