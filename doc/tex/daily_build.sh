#!/bin/bash
cd /Users/yoachim/gitRepos/AstroHireNetwork/doc/tex
if test `find writeup.tex -mmin -1440`
then
    pdflatex writeup
    bibtex writeup
    pdflatex writeup
    pdflatex writeup
    cp writeup.pdf /Users/yoachim/www/Share/Daily_build/.
    web_up
fi
