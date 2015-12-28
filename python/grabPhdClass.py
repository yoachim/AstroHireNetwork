import numpy as np
import ads
import networkx as nx
import numpy as np
import difflib
import datetime

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
    # Check if a list of publications includes at least one in
    # an "astronomy journal".  Maybe also AAS or IAU meeting abstract.
    if not hasattr(inAstroJ, 'journalList'):
        inAstroJ.journalList = ['Astronomy and Astrophysics',
                                'The Astrophysical Journal',
                                'The Astronomical Journal' #XXX-add more
    ]

    # If it's a string, just test it
    if type(toTest) is str:
        return toTest in inAstroJ.journalList
    else:
    # Else, loop through
        for journal in toTest:
            if journal.pub in inAstroJ.journalList:
                return True
    return False


def authSimple(author):
    """
    reduce a name string to Last, FI
    """
    result = ''
    if ',' in author:
        temp = author.split(',')
        result = temp[0]+', '+temp[1].strip()[0]
    else:
        temp = author.split(' ')
        result = temp[-1] + ', '+temp[0][0]
    return result


def authorGroup(articleList, anchorArticle, anchorAuthor):
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
        refs = article.references
        article.refbibcodes = [ref.bibcode for ref in refs]
        article.authorSet = set([authSimple(author)  for author in article.author if (len(author) > 4)])

    # Create graph
    paperGraph = nx.Graph()
    # Add the bibcodes as nodes
    paperGraph.add_nodes_from(articleBibcodes)
    nArticles = len(articleList)
    for i in range(nArticles-1):
        for j in np.arange(nArticles-i)+i:
            match = checkAuthorMatch(articleList[i], articleList[j],
                                     authorName=anchorAuthor)
            if match:
                paperGraph.add_edge(articleList[i].bibcode,
                                    articleList[j].bibcode)

    # Find all the papers that are connected to the articleNode
    connectedPapers = nx.node_connected_component(paperGraph, anchorArticle.bibcode)
    # Now I have the bibcodes for all the papers that are connected
    # to the anchorArticle

    # Convert to a list of ads article objects to pass back
    result = [bibcodeDict[paperbibcode] for paperbibcode in connectedPapers]

    return result, paperGraph

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
                     yearGap=2, nCommonRefs=9,  nCommonAuths=3,
                     matchThresh=0.70):
    """
    Check if two articles are probably from the same author.

    I think they are if:
    1) They are published within yearGap of eachother, from the same location
    or
    2) They share nCommonRefs or more
    or
    3) They share nCommonAuths or more

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

    # If published within yearGap from same location
    if np.abs(int(article1.year)-int(article2.year)) <= yearGap:
        aff1 = None
        aff2 = None
        for name, aff in zip(article1.author,article1.aff):
            if authSimple(name) == authSimple(authorName):
                aff1 = affClean(aff)
        for name, aff in zip(article2.author,article2.aff):
            if authSimple(name) == authSimple(authorName):
                aff2 = affClean(aff)
        if (aff1 is not None) & (aff2 is not None):
            if checkAffMatch(aff1,aff2,matchThresh=matchThresh):
                return True
    # If they share nCommonRefs
    if (hasattr(article1,'refbibcodes') & hasattr(article2,'refbibcodes')):
        if len(set(article1.refbibcodes) & set(article2.refbibcodes)) >= nCommonRefs:
            return True
    # If they share nCommonAuths
    commonAuthors = set([authSimple(auth) for auth in
                         article1.author]) & set([authSimple(auth) for
                                                  auth in article2.author])
    if len(commonAuthors) >= nCommonAuths:
        return True

    return result

def usAffCheck(article):
    """
    check that the affiliation on an article is in the US
    """
    # Maybe do a split on ',' and '-' and only take the first part?
    # make sure to compare in a case-insensitive way.


def grabPhdClass(year):
    """
    Return a list of all the phd thesis from a given year
    """
    # OK, now how do I get all of them?--boom, rows='all'
    ack = list(ads.query('bibstem:*PhDT', dates=year, database='astronomy', rows='all'))
    return ack

def authorsPapers(author, year=None):
    ack = list(ads.query(authors=author, dates=year, database='astronomy', rows='all'))
    return ack

def phdArticle2row(phdArticle, yearsPrePhD=7):
    """
    Take an ads article object and return a dict of information with keys:
    [name, phd year, phd bibcode, phd.aff, latest paper bibcode, latest year,
    latest aff, latest 1st author bibcode, latest 1st year, latest 1st aff,
    largest publication gap]

    Note:  Currently not making any cut based on peer-review. Thus, latest 1st author
    paper could be a AAS poster, SPIE paper, arXive posting, etc.

    XXX-consider pulling some metrics from ADS and putting them in the row.
    """
    result = {}
    resultKeys = ['name', 'phd year', 'phd bibcode', 'phd aff',
                  'latest year',
                  'latest aff', 'latest 1st year',
                  'latest 1st aff', 'largest publication gap',
                  'noAstroJournal', 'nonUS']

    maxYear = datetime.date.today().year
    minYear = int(phdArticle.year) - yearsPrePhD
    years = [minYear,maxYear] #range(minYear, maxYear+1) #str(minYear)+'-%i'% maxYear

    result['name'] = authSimple(phdArticle.author[0])
    result['phd year'] = int(phdArticle.year)
    result['phd aff'] = phdArticle.aff[0]
    result['phd bibcode'] = phdArticle.bibcode
    result['phd aff'] = phdArticle.aff[0]

    # Check that phd is from the US
    if not checkUSAff(phdArticle.aff[0]):
        result['nonUS'] = True
        return result

    # Query for all the papers by this author name
    paperList = authorsPapers(phdArticle.author[0], year=years)

    # Check that there's an astro paper in here
    if not inAstroJ(paperList):
        result['noAstroJournal'] = True
        return result

    # Find all the papers linked to the PHD in question
    linkedPapers, linkedGraph = authorGroup(paperList, phdArticle,
                                            authSimple(phdArticle.author[0]))

    # Make sure there's still a publication in an astro journal
    if not inAstroJ(linkedPapers):
        result['noAstroJournal'] = True
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
        linkedYears.append(int(paper.year))
        if int(paper.year) > int(latestPaper.year):
            latestPaper = paper

        if authSimple(paper.author[0]) == authSimple(phdArticle.author[0]):
            linked1stA.append(paper)
            linked1stAYears.append(int(paper.year))
            if int(paper.year) > int(latest1stApaper.year):
                latest1stApaper = paper
        paperDate =int(paper.pubdate.split('-')[1])
        if paperDate < 1:
            paperDate = 1
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


def test2():
    name = 'Yoachim, P'
    myPapers = authorsPapers(name)
    # Try linking my publications
    mineLinked, myG = authorGroup(myPapers, myPapers[-1], name)
    years = [float(paper.year) for paper in myPapers]
    nx.draw_spring(myG, node_color=np.array(years))

    #figure out which ones are not linked
    notLinked = [paper for paper in myPapers if paper not in mineLinked]
    for paper in notLinked:
        print paper

def testRow():
    myphd = list(ads.query('bibcode:2007PhDT.........3Y', database='astronomy', rows='all'))[0]
    phdArticle2row(myphd)
