import numpy as np
import ads
import networkx as nx
import numpy as np
import difflib
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from leven import levenshtein

def checkUSAff(affil):
    """
    Check if an affiliation is in the USA.

    returns
    -------
    bool
    """
    if not hasattr(checkUSAff,'usinst'):
        checkUSAff.usinst = np.genfromtxt('simpleUSList.dat', dtype='|S50',
                                          delimiter='$$', comments='#')
        checkUSAff.usinst = [aff.strip().lower() for aff in checkUSAff.usinst]

    if affil.lower() in checkUSAff.usinst:
        return True
    for inst in checkUSAff.usinst:
        if inst in affil.lower():
            return True
    return False

def inAstroJ(toTest):
    """
    Demand that at at least one article be in an 'astronomy' venue.
    """
    # Check if a list of publications includes at least one in
    # an "astronomy journal".  Maybe also AAS or IAU meeting abstract.
    if not hasattr(inAstroJ, 'journalList'):
        inAstroJ.journalList = ['Astronomy and Astrophysics', 'A&A',
                                'Astrophysical Journal', 'AJ'
                                'Astronomical Journal' 'ApJ',
                                'Monthly Notices of the Royal Astronomical Society','MNRAS',
                                'Icarus',
                                'American Astronomical Society', 'AAS',
                                'International Astronomical Union', 'IAU'
    ]
        inAstroJ.journalList = [j.lower() for j in inAstroJ.journalList]

    # If it's a string, just test it
    if type(toTest) is str:
        result = False
        for journal in inAstroJ.journalList:
            if journal in toTest.pub:
                result = True
        return result
    else:
        # The unique list of publication names
        pubs = []
        for article in toTest:
            if hasattr(article, 'pub'):
                pubs.append(article.pub.lower())
                # XXX--wait, I can just merge all these together, no need to do a nested loop.
        for pub in pubs:
            for astroPub in inAstroJ.journalList:
                if pub in astroPub:
                    return True
    return False


def authSimple(author):
    """
    reduce a name string to Last, FI
    """
    result = ''
    if ',' in author:
        temp = author.replace(',,',',').split(',')
        temp0 = temp[0]
        temp1 = temp[1].strip()
        if len(temp1) > 0:
            temp1 = temp1[0]
        result = temp0+', '+temp1
    else:
        temp = author.split(' ')
        result = temp[-1] + ', '+temp[0][0]
    result = result.lower()
    # Eliminate any unexpected upper-case letters
    result = result[0].upper()+result[1:-1]+result[-1].upper()
    return result


def authorGroup(articleList, anchorArticle, anchorAuthor,
                absMatchLimit=0.5, titleMatchLimit=0.6, unconnLimit=5):
    """
    Given a list of articles, go through and find the ones that are connected to anchorArticle.

    Return the list of papers and the paper network graph that was constructed
    """
    # so I can do article.references to get the list of ads.Article references.
    # Looking at http://adsabs.github.io/help/actions/visualize/#paper-network
    # Maybe I should just resort to a graph network. Make a node for each paper. Make an edge if two papers share more than N references in common, or 3 or more authors in common, or an affiliation and year+/-2?

    # to find common elements of two lists:
    # common = set(b1) & set(b2)

    if anchorArticle not in articleList:
        articleList.append(anchorArticle)

    # Use these as the nodes in the graph
    articleBibcodes = [article.bibcode for article in articleList]
    # Make a handy dict for later:
    bibcodeDict = {}
    for article in articleList:
        bibcodeDict[article.bibcode] = article

    # For each article, add an atribute that is a list of
    # bibcodes for that article's references
    # and an atribute that is the set of authors
    # I should really make a dict, but it's sooo compact to just add atributes
    for article in articleList:
    #    refs = article.references
    #    article.refbibcodes = [ref.bibcode for ref in refs]
        article.authorset = set([authSimple(author)  for author in article.author])

    # Create graph
    paperGraph = nx.Graph()
    # Add the bibcodes as nodes
    paperGraph.add_nodes_from(articleBibcodes)
    nArticles = len(articleList)

    # Do the abstract analysis here to try and speed it up
    abstracts = []
    titles = []
    for paper in articleList:
        if hasattr(paper,'abstract'):
            abstracts.append(paper.abstract)
        else:
            abstracts.append('')
        if hasattr(paper,'title'):
            titles.append(paper.title[0])
        else:
            titles.append('')
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(abstracts)
    abstractArray = (tfidf * tfidf.T).A

    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(titles)
    titleArray = (tfidf * tfidf.T).A


    for i in range(nArticles-1):
        for j in np.arange(nArticles-i)+i:
            match = False
            if abstractArray[i][j] > absMatchLimit:
                match = True
            elif titleArray[i][j] > titleMatchLimit:
                match = True
            if not match:
                match = checkAuthorMatch(articleList[i], articleList[j],
                                         authorName=anchorAuthor)
            if match:
                paperGraph.add_edge(articleList[i].bibcode,
                                    articleList[j].bibcode)

    # Find all the papers that are connected to the articleNode
    connectedBibcodes = nx.node_connected_component(paperGraph, anchorArticle.bibcode)
    # Convert to a list of ads article objects to pass back
    connectedPapers = [bibcodeDict[paperbibcode] for paperbibcode in connectedBibcodes]
    # Now I have the bibcodes for all the papers that are connected
    # to the anchorArticle

    return connectedPapers, paperGraph

def affClean(aff):
    """
    Clean an affiliation name so that it doesn't have common words that might trigger a false match
    """

    genericWords = ['of', 'the', 'University', 'Department', 'Dept',
                    'Univ', 'Lab', 'Laboratory', 'Observatory',', ']
    result = aff.lower()
    for word in genericWords:
        result = result.replace(word.lower(),'')
    return result.strip()

def checkAffMatch(aff1,aff2, matchThresh=0.70):
    """
    See if two affiliations are similar enough that we think they match

    Make them lower case so things will work since some affiliations
    end up as all caps.
    """
    result = False
    # Bail out if either one is None
    if aff1 is None:
        return False
    if aff2 is None:
        return False
    # Bail out if either one is a '-'
    if (aff1 == '-') | (aff2 == '-'):
        return False

    # If they just match
    if aff1.lower() == aff2.lower():
        return True
    # If one is contained in the other (e.g., 'Univ X' and 'Univ X, Anytown, ST, 876644')
    if aff1.lower() in aff2.lower():
        return True
    if aff2.lower() in aff1.lower():
        return True
    # If they fuzzy compare to be close enough.
    if difflib.SequenceMatcher(None, affClean(aff1),affClean(aff2)).ratio() > matchThresh:
        return True

    return result


def checkAuthorMatch(article1,article2,authorName=None,
                     yearGap=2, nCommonAuths=3,
                     matchThresh=0.70, absMatchLimit=0.5,
                     titleMatchLimit=0.5, keywordMatchTol=2):
    """
    Check if two articles are probably from the same author.

    I think they are if:
    1) They are published within yearGap of eachother, from the same location
    or
    2) They share nCommonRefs or more
    or
    3) They share nCommonAuths or more
    or
    4) Author lists are >1 and have the same names.
    or
    5) Author of interest is spelled exactly the same, and they share 2+ keywords

    matchThresh sets the theshold for doing fuzzy string comparison with the
    affiliation names (so, 'Univeristy of Washington' will match
    'University of Washington, Astronomy Department'

    returns
    -------
    bool

    """
    result = False
    # If any of the criteria match, return True and bail out

    if authorName is None:
        authorName = authSimple(article1.author[0])

    # If author list is >1 and identical
    if len(article1.authorset) > 1:
        if article1.authorset == article2.authorset:
            return True

    # If published within yearGap from same location
    if hasattr(article1,'year') & hasattr(article2,'year'):
        if np.abs(int(article1.year)-int(article2.year)) <= yearGap:
            aff1 = None
            aff2 = None
            lDists = [levenshtein(unicode(authorName),unicode(authSimple(name))) for
                      name in article1.author]
            good = np.where(lDists == np.min(lDists))[0]
            # Can't tell which one is author, can't link it up.
            if np.size(good) > 1:
                return False
            if lDists[good] < 3:
                aff1 = affClean(article1.aff[good])
            lDists = [levenshtein(unicode(authorName),unicode(authSimple(name))) for
                      name in article2.author]
            good = np.where(lDists == np.min(lDists))[0]
            if np.size(good) > 1:
                return False
            if lDists[good] < 3:
                aff2 = affClean(article2.aff[good])
            if (aff1 is not None) & (aff2 is not None):
                if checkAffMatch(aff1,aff2,matchThresh=matchThresh):
                    return True

    # Check if they have enough common authors
    commonAuthors = article1.authorset.intersection(article2.authorset)
    if len(commonAuthors) >= nCommonAuths:
        return True

    # If the keywords are in common
    if len(set(article1.keyword) & set(article2.keyword)) > keywordMatchTol:
        # If the author is spelled exactly the same, and there are matching keywords
        a1 = [author for author in article1.author if authSimple(author) == authSimple(authorName)]
        a2 = [author for author in article2.author if authSimple(author) == authSimple(authorName)]
        if (len(a1) == 1) & (len(a2) ==1):
            # If the names match exactly
            if a1[0] == a2[0]:
                return True

    return result

def grabPhdClass(year):
    """
    Return a list of all the phd thesis from a given year
    """
    # OK, now how do I get all of them?--boom, rows='all'
    ack = list(ads.query('bibstem:*PhDT', dates=year, database='astronomy', rows='all'))
    return ack

def authorsPapers(author, year=None):
    # Getting a problem with large querie I think
    try:
        result = list(ads.query(authors=author, dates=year, database='astronomy', rows='all'))
    except:
        print 'failed to query author: %s' % author.encode('utf-8')
        result = []
    return result

def phdArticle2row(phdArticle, yearsPrePhD=7, verbose=False, checkUSA=True,
                   justKeys=False, plot=False, returnNetwork=False, returnLinkedPapers=False):
    """
    Take an ads article object and return a dict of information with keys:
    [name, phd year, phd bibcode, phd.aff, latest paper bibcode, latest year,
    latest aff, latest 1st author bibcode, latest 1st year, latest 1st aff,
    largest publication gap]

    Note:  Currently not making any cut based on peer-review. Thus, latest 1st author
    paper could be a AAS poster, SPIE paper, arXive posting, etc.

    XXX-consider pulling some metrics from ADS and putting them in the row.
    """
    if verbose:
        print 'searching for papers linked to:', phdArticle


    result = {}
    resultKeys = ['name', 'phd year', 'phd bibcode', 'phd aff',
                  'latest year',
                  'latest aff', 'latest 1st year',
                  'latest 1st aff', 'largest publication gap',
                  'numRecords','numLinked', 'uniqueName', 'latest year unlinked',
                  'noAstroJournal', 'nonUS']

    if justKeys:
        return resultKeys


    for key in resultKeys:
        result[key] = None

    maxYear = datetime.date.today().year
    minYear = int(phdArticle.year) - yearsPrePhD
    years = [minYear,maxYear] #range(minYear, maxYear+1) #str(minYear)+'-%i'% maxYear

    result['name'] = authSimple(phdArticle.author[0])
    result['phd year'] = int(phdArticle.year)
    result['phd aff'] = phdArticle.aff[0]
    result['phd bibcode'] = phdArticle.bibcode
    result['phd aff'] = phdArticle.aff[0]


    # Check that phd is from the US
    if checkUSA:
        if not checkUSAff(phdArticle.aff[0]):
            result['nonUS'] = True
            if verbose:
                print '%s does not test as a USA affiliation' % phdArticle.aff[0].encode('utf-8')
            return result

    # Query for all the papers by this author name
    paperList = authorsPapers(phdArticle.author[0], year=years)

    if verbose:
        print 'Found %i papers' % len(paperList)

    result['numRecords'] = len(paperList)
    # Check that there's an astro paper in here
    if not inAstroJ(paperList):
        result['noAstroJournal'] = True
        if verbose:
            print 'Did not find an astro paper in results'
        return result

    # Find all the papers linked to the PHD in question
    linkedPapers, linkedGraph = authorGroup(paperList, phdArticle,
                                            authSimple(phdArticle.author[0]))

    # Check if the


    if returnLinkedPapers:
        return linkedPapers
    result['numLinked'] = len(linkedPapers)
    if plot:
        years = [float(paper.year) for paper in linkedPapers]
        nx.draw_spring(linkedGraph)#, node_color=np.array(years))

    if verbose:
        print 'Found %i papers linked to phd' % len(linkedPapers)
    # Make sure there's still a publication in an astro journal
    if not inAstroJ(linkedPapers):
        result['noAstroJournal'] = True
        if verbose:
            print 'Did not find an astro paper in linked results'
        return result

    linkedYears = []
    linked1stA = []
    linked1stAYears = []
    latestPaper = linkedPapers[0]
    latest1stApaper = phdArticle

    latestAff = phdArticle.aff[0]
    affDate = phdArticle.pubdate.split('-')
    month = int(affDate[1])
    if month < 1:
        month = 1
    affDate = datetime.date(year=int(phdArticle.year), month=month, day=1)

    for paper in linkedPapers:
        if hasattr(paper, 'year'):
            linkedYears.append(int(paper.year))
            if int(paper.year) > int(latestPaper.year):
                latestPaper = paper

        if authSimple(paper.author[0]) == authSimple(phdArticle.author[0]):
            linked1stA.append(paper)
            if hasattr(paper, 'year'):
                linked1stAYears.append(int(paper.year))
                if int(paper.year) > int(latest1stApaper.year):
                    latest1stApaper = paper
        paperDate =int(paper.pubdate.split('-')[1])
        if paperDate < 1:
            paperDate = 1
        if hasattr(paper,'year'):
            paperDate = datetime.date(int(paper.year), paperDate, 1)

            if paperDate >= affDate:
                for auth,aff in zip(paper.author, paper.aff):
                    if authSimple(auth) == authSimple(phdArticle.author[0]):
                        if aff is not None:
                            if len(aff) > 3:
                                latestAff = aff
                                affYear = int(paper.year)


    result['largest publication gap'] = np.max(np.diff(np.sort(linkedYears)))
    result['latest year'] = int(latestPaper.year)
    result['latest 1st year'] = int(latest1stApaper.year)
    result['latest aff'] = latestAff

    allYears = [int(paper.year) for paper in paperList if hasattr(paper,'year')]
    result['latest year unlinked'] = np.max(allYears)

    # Test to see if this is the only person with this name and a phd in astro
    ack = list(ads.query('bibstem:"*PhDT", author:"%s"' % authSimple(phdArticle.author[0]),
                         database='astronomy'))
    titles = []
    if len(ack) > 1:
        # Make sure the titles are different
        titles = set([paper.title[0].lower() for paper in ack])
    if len(titles) > 1:
        if verbose:
            print authSimple(phdArticle.author[0])+' returns multiple PhDT.'
        result['uniqueName'] = False
    else:
        result['uniqueName'] = True

    if returnNetwork:
        return result, linkedGraph
    return result


def test1():
    # Year now
    maxYear = 2015
    # How many years pre-phd to search for papers
    yearsPrePhD = 7
    phdYear = 2002

    test = grabPhdClass(phdYear)

    uwGrads = []
    for article in test:
        if 'UNIVERSITY OF WASHINGTON' in article.aff[0]:
            uwGrads.append(article)

    # can I do an author query with the
    article = uwGrads[-1]
    years = str(int(article.year)-yearsPrePhD)+'-%i'% maxYear
    paperList = authorsPapers(article.author[0], year=years)

def test15():
    """
    Let's try to make some output
    """
    resultKeys = ['name', 'phd year', 'phd bibcode', 'phd aff',
                  'latest year',
                  'latest aff', 'latest 1st year',
                  'latest 1st aff', 'largest publication gap',
                  'noAstroJournal', 'nonUS']

    f = open('test15out.dat', 'w')
    phdYear = 2002
    test = grabPhdClass(phdYear)
    uwGrads = []
    for article in test:
        if 'UNIVERSITY OF WASHINGTON'.lower() in article.aff[0].lower():
            uwGrads.append(article)

    # Let's just crop down for a minute
    print 'number of UW grads = %i' % len(uwGrads)
    ack = [uwGrads[0], uwGrads[-1], uwGrads[5], uwGrads[1]]
    uwGrads = ack
    for phd in uwGrads:
        print 'Generating row for:', phd
        row = phdArticle2row(phd, verbose=True)
        out = ''
        for key in resultKeys:
            out += str(row[key])+'; '
        print >>f, out

    f.close()


def test2(name='Yoachim, P'):
    myPapers = authorsPapers(name)
    # Try linking my publications
    mineLinked, myG = authorGroup(myPapers, myPapers[-1], name)
    years = [float(paper.year) for paper in myPapers]
    nx.draw_spring(myG, node_color=np.array(years))

    #figure out which ones are not linked
    #notLinked = [paper for paper in myPapers if paper not in mineLinked]
    #for paper in notLinked:
    #    print paper

def testRow():
    myphd = list(ads.query('bibcode:2007PhDT.........3Y', database='astronomy', rows='all'))[0]
    phdArticle2row(myphd)

def testPerson(name, phdyear):
    """
    Test a random person and see if it gives the correct answer
    """

    phdA =  list(ads.query('bibstem:*PhDT', authors=name, dates=phdyear, database='astronomy', rows='all'))

    result = phdArticle2row(phdA[0], checkUSA=False, verbose=True, plot=True)


    print 'PhD Institution: %s' % result['phd aff']
    print 'Latest Institution: %s' % result['latest aff'].encode('utf-8')
    print 'Last year: %i' % result['latest year']

def testOverlap():
    """
    See if there is any overlap betwen linked list for two identical authors
    """

    name = 'Williams, B'
    year = 2002
    phd1 =  list(ads.query('bibstem:*PhDT', authors=name, dates=year,
                               database='astronomy', rows='all'))[0]
    year = 2010
    phd2 = list(ads.query('bibstem:*PhDT', authors=name, dates=year,
                               database='astronomy', rows='all'))[0]

    list1 = phdArticle2row(phd1, returnLinkedPapers=True)
    list2 = phdArticle2row(phd2, returnLinkedPapers=True)

    overlap = list(set(list1).intersection(list2))
    print 'number of overlap papers in linked lists = %i' % len(overlap)
