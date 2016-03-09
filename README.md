# AstroHireNetwork

A little side project to look at how phd-overproduction has impacted the publication lifetime of astronomers.

Overview
--------

The process here is that I query for all the PhDs in a given year. Then I select only those that are from the USA. Then, for each author I do an author query and build a graph network connecting the papers together (to keep from linking people with common names together).  Next, I check that there is at least one paper in the connected network that is an Astronomy journal.  Finally, I record some stats about the network (phd year, year of last entry, year of last 1st author entry, etc).

The code is a bit messy since this was a project that grew organically while I was learning lots of new things, but my hope is that it can be refactored into a useful tool that others can expand on.  It would be great if other folks wanted to look at other countries, look at gender differences in career lengths, look at institution networks, etc.

The main result so far is that the publication lifetime of PhDs appears to have collapsed after the 2008 crash. My goal is to get this published in a peer-reviewed journal.

Collaborators welcome.



Dependencies:
-------------
* You need an ADS API developer key, follow directions here to get one: https://github.com/adsabs/adsabs-dev-api
* ADS client from here: https://github.com/andycasey/ads
* networkx, sklearn, numpy, matplotlib (all come with anaconda python)
* levenshtein (pip install leven)

To Run:
-------
To generate the rows for a given PhD cohort:
```
runYear.py 2001
```
or a bunch
```
seq 1995 2013 | xargs -I'{}' runYear.py '{}'
```
Then combine all the years:
```
combine.sh
```
Make plots:
```
makePlots.py --plot1 --plot2 --network
```
