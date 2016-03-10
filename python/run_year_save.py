#! /usr/bin/env python
from grabPhdClass import grabPhdClass, checkUSAff, authorsPapers, authSimple
import os,argparse
import numpy as np
import glob
import datetime
import ads

def article2dict(article):
    """
    Convert an article object to a simple dict
    """
    keys2copy = ['aff', 'pub', 'abstract', 'author', 'first_author',
                 'bibcode', 'keyword', 'year', 'title']
    result = {}
    for key in keys2copy:
        result[key] = getattr(article,key)
    return result



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate save files for every phd. Then the networks can be remade later")
    parser.add_argument("year", type=int, help="year to query")

    args = parser.parse_args()

    outDir = 'output/%s' % args.year
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    print 'Querying for year %i' % args.year
    phdArticles = grabPhdClass(args.year)
    print 'Found %i articles' % len(phdArticles)


    yearsPrePhD=7
    now = datetime.datetime.now()
    # XXX- read in here things that have already been done
    fileList = glob.glob(os.path.join(outDir, '*.npz'))
    doneBibcodes = [os.path.basename(filename).replace('.npz','').replace('_','.')
                    for filename in fileList]
    phdArticles = [article for article in phdArticles if article.bibcode not in doneBibcodes]
    print '%i not yet searched for' % len(phdArticles)

    for phd in phdArticles:
        flags = {}
        if not checkUSAff(phd.aff[0]):
            result = [article2dict(phd)]
            flags['nonUS'] = True
            try:
                print '%s not a US inst' % phd.aff[0]
            except:
                print 'something with a wacky character is not a US inst'
        else:
            try:
                print 'quering for %s' % phd.author[0].encode('utf-8')
            except:
                print "quering for some name that can't print"
            papers = authorsPapers(phd.author[0].encode('utf-8'),
                                   years='%i-%i' % (int(phd.year)-yearsPrePhD,
                                                    now.year) )
            phdDict = article2dict(phd)
            result = [article2dict(paper) for paper in papers]
            # Make sure the phd is in there!
            if phdDict not in result:
                result.append(phdDict)
            flags['nonUS'] = False

            # Need to add a search for similar named phds
            ack = list(ads.SearchQuery(q='bibstem:"*PhDT" author:"%s"' % authSimple(phd.author[0].encode('utf-8')),
                                       database='astronomy'))
            if len(ack) > 1:
                titles = set([paper.title[0].lower() for paper in ack if hasattr(paper, 'title')])
                if len(titles) > 1:
                    flags['uniqueName'] = False
                else:
                    flags['uniqueName'] = True
            else:
                flags['uniqueName'] = True


        savefile = phd.bibcode.replace('.','_')+'.npz'
        np.savez(os.path.join(outDir ,savefile), result=result, flags=flags)
