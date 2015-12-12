import numpy as np
import ads


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
paperList = authorsPapers(article.author, year=years)

# Now, I need to go through the list and decide which ones belong to the PHD author


# What do I want my final output to be?
# (name, phd year, phd bibcode, phd.aff, latest paper bibcode, latest year, latest aff, latest 1st author bibcode, latest 1st year, latest 1st aff)

def authorGroup(articleList, articleNode):
    """
    Given a list of articles, go through and find the ones that are connected to articleNode.

    """

    # so I can do article.references to get the list of ads.Article references.
    # Looking at http://adsabs.github.io/help/actions/visualize/#paper-network
    # Maybe I should just resort to a graph network. Make a node for each paper. Make an edge if two papers share more than N references in common, or 3 or more authors in common, or an affiliation and year+/-2?

    # to find common elements of two lists:
    # common = set(b1) & set(b2)

    # Find references in each paper
    refsList = [article.refrences for article in articleList]
    bibcodeList = []
    # Pull out just the bibcodes fo the references
    for refs in resfList:
        bibList = [ref.bibcode for ref in refs]
        bibcodeList.append(bibList)
