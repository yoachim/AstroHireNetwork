#! /usr/bin/env python
from grabPhdClass import grabPhdClass, phdArticle2row
import os,argparse



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a database of astro phds for a given year")
    parser.add_argument("year", type=int, help="year to query")

    args = parser.parse_args()

    outDir = 'output'
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    f = open(os.path.join(outDir,str(args.year)+'.dat'),'w' )

    resultKeys = phdArticle2row(None, justKeys=True)
    header = ''
    for key in resultKeys:
        header += '; key'
        header = header[2:]

    print >>f, header

    print 'Querying for year %i' % args.year
    phdArticles = grabPhdClass(args.year)
    print 'Found %i articles' % len(phdArticles)

    for phd in phdArticles:
        print 'Generating row for:', phd
        row = phdArticle2row(phd, verbose=True)
        out = ''
        for key in resultKeys:
            out += str(row[key])+'; '
        print >>f, out

    f.close()
