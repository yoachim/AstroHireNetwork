# AstroHireNetwork

A little side project to look at how phd-overproduction has impacted the publication lifetime of astronomers.

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
