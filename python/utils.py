import numpy as np
import ads
import networkx as nx
import numpy as np
import difflib
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from leven import levenshtein



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
                                'Publications of the Astronomical Society of the Pacific', 'PASP',
                                 #'Icarus',
                                #'American Astronomical Society', #'AAS',
                                #'International Astronomical Union'#, 'IAU'
    ]
        inAstroJ.journalList = [j.lower() for j in inAstroJ.journalList]

    # If it's a string, just test it
    if type(toTest) is str:
        result = False
        for journal in inAstroJ.journalList:
            if journal in toTest:
                result = True
            if toTest in journal:
                result = True
        return result
    else:
        # The unique list of publication names
        pubs = []
        for article in toTest:
            if article['pub'] is not None:
                pubs.append(article['pub'].lower())
        # Can't just do set.intersection, because need to pass things like AJ Letters
        for pub in pubs:
            for astroPub in inAstroJ.journalList:
                if pub in astroPub:
                    return True
                if astroPub in pub:
                    return True
    return False




def authSimple(author):
    """
    reduce a name string to Last, FI
    """
    result = ''
    if author is None:
        return result
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
        authorName = authSimple(article1['author'][0])

    # If author list is >1 and identical
    if len(article1['authorset']) > 1:
        if article1['authorset'] == article2['authorset']:
            return True

    # If published within yearGap from same location
    if (article1['year'] is not None) & (article2['year'] is not None) & (article1['author'] is not None) & (article2['author'] is not None):
        if np.abs(int(article1['year'])-int(article2['year'])) <= yearGap:
            aff1 = None
            aff2 = None
            lDists = [levenshtein(unicode(authorName),unicode(authSimple(name))) for
                      name in article1['author']]
            good = np.where(lDists == np.min(lDists))[0]
            # Can't tell which one is author, can't link it up.
            if np.size(good) > 1:
                return False
            if lDists[good] < 3:
                aff1 = affClean(article1['aff'][good])
            lDists = [levenshtein(unicode(authorName),unicode(authSimple(name))) for
                      name in article2['author']]
            good = np.where(lDists == np.min(lDists))[0]
            if np.size(good) > 1:
                return False
            if lDists[good] < 3:
                aff2 = affClean(article2['aff'][good])
            if (aff1 is not None) & (aff2 is not None):
                if checkAffMatch(aff1,aff2,matchThresh=matchThresh):
                    return True

    # Check if they have enough common authors
    commonAuthors = article1['authorset'].intersection(article2['authorset'])
    if len(commonAuthors) >= nCommonAuths:
        return True

    # If the keywords are in common
    if (article1['keyword'] is not None) & (article2['keyword'] is not None):
        if (len(set(article1['keyword']) & set(article2['keyword']))) > keywordMatchTol:
            if article1['author'] is not None:
                if article2['author'] is not None:
                    # If the author is spelled exactly the same, and there are matching keywords
                    a1 = [author for author in article1['author'] if authSimple(author) == authSimple(authorName)]
                    a2 = [author for author in article2['author'] if authSimple(author) == authSimple(authorName)]
                    if (len(a1) == 1) & (len(a2) ==1):
                        # If the names match exactly
                        if a1[0] == a2[0]:
                            return True

    return result

def paper_network(articleList, anchorArticle, anchorAuthor,
                  absMatchLimit=0.5, titleMatchLimit=0.6, unconnLimit=5):
    """
    Given a list of articles, go through and find the ones that are connected to anchorArticle.

    Return the list of papers and the paper network graph that was constructed
    """
    if anchorArticle not in articleList:
        articleList.append(anchorArticle)

    # Use these as the nodes in the graph
    articleBibcodes = [article['bibcode'] for article in articleList]
    # Make a handy dict for later:
    bibcodeDict = {}
    for article in articleList:
        bibcodeDict[article['bibcode']] = article


    for article in articleList:
        if article['author'] is not None:
            article['authorset'] = set([authSimple(author) for author in article['author'] if author is not None])
        else:
            article['authorset'] = set([])

    # Create graph
    paperGraph = nx.Graph()
    # Add the bibcodes as nodes
    paperGraph.add_nodes_from(articleBibcodes)
    nArticles = len(articleList)

    # Do the abstract analysis here to try and speed it up
    abstracts = []
    titles = []
    for paper in articleList:
        if paper['abstract'] is not None:
            abstracts.append(paper['abstract'])
        else:
            abstracts.append('')
        if paper['title'] is not None:
            titles.append(paper['title'][0])
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
                if (articleList[i] is not None) & (articleList[j] is not None):
                    match = checkAuthorMatch(articleList[i], articleList[j],
                                             authorName=anchorAuthor)
            if match:
                paperGraph.add_edge(articleList[i]['bibcode'],
                                    articleList[j]['bibcode'])

    # Find all the papers that are connected to the articleNode
    connectedBibcodes = nx.node_connected_component(paperGraph, anchorArticle['bibcode'])
    # Convert to a list of ads article objects to pass back
    connectedPapers = [bibcodeDict[paperbibcode] for paperbibcode in connectedBibcodes]
    # Now I have the bibcodes for all the papers that are connected
    # to the anchorArticle

    return connectedPapers, paperGraph
