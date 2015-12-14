import numpy as np
import ads
import networkx as nx
import numpy as np


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


def authorGroup(articleList, articleNode):
    """
    Given a list of articles, go through and find the ones that are connected to articleNode.
    """
    # so I can do article.references to get the list of ads.Article references.
    # Looking at http://adsabs.github.io/help/actions/visualize/#paper-network
    # Maybe I should just resort to a graph network. Make a node for each paper. Make an edge if two papers share more than N references in common, or 3 or more authors in common, or an affiliation and year+/-2?

    # to find common elements of two lists:
    # common = set(b1) & set(b2)

    if articleNode not in articleList:
        articleList.append(articleNode)

    articleBibcodes = [article.bibcode for article in articleList]

    # For each article, add an atribute that is a list of
    # bibcodes for that article's references
    # and an atribute that is the set of authors
    # I should really make a dict, but it's sooo compact to just add atributes
    for article in articleList:
        refs = article.refrences
        article.refbibcodes = [ref.bibcode for ref in refs]
        article.authorSet = set([authSimple(author)  for author in article.author if (len(author) > 4)])

    # Create graph
    paperGraph = nx.Graph()
    # Add the bibcodes as nodes
    paperGraph.add_node(articleBibcodes)
    nArticles = len(articleList)
    for i in range(nArticles):
        for j in range(nArticles-i-1)+i+1:
            match = checkAuthorMatch(articleList[i], articleList[j])
            if match:
                paperGraph.add_edge(articleList[i].bibcode,
                                    articleList[j].bibcode)

    # Find all the papers that are connected to the articleNode
    #XXX


def checkAuthorMatch(article1,article2,authorName=None,
                     yearGap=2, nCommonRefs=5 ):
    """
    Check if two articles are probably from the same author.

    I think they are if:
    1) They are published within yearGap of eachother, from the same location
    or
    2) They share nCommonRefs or more
    or
    3) They share nCommonAuths or more
    """
    result = False
    # If any of the criteria match, return True and bail out
    if authorName is None:
        authorName = authSimple(article1.author[0])

    # If published within yearGap from same location
    if np.abs(int(artcle1.year)-int(article2.year)) <= yearGap:
        if article1.aff == article2.aff:
            return True
    # If they share nCommonRefs


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
    ack = list(ads.query(authors=author, year=year, database='astronomy', rows='all'))
    return ack

# Year now
maxYear = 2015
# How many years pre-phd to search for papers
yearsPrePhD = 7

test = grabPhdClass(2002)

uwGrads = []
for article in test:
    if 'UNIVERSITY OF WASHINGTON' in article.aff[0]:
        uwGrads.append(article)

# can I do an author query with the
article = uwGrads[-1]
years = str(int(article.year)-yearsPrePhD)+'-%i'% maxYear
paperList = authorsPapers(article.author[0], year=years)

# Now, I need to go through the list and decide which ones belong to the PHD author


# What do I want my final output to be?
# (name, phd year, phd bibcode, phd.aff, latest paper bibcode, latest year, latest aff, latest 1st author bibcode, latest 1st year, latest 1st aff)
