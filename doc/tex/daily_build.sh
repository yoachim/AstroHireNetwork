#!/bin/bash

# Make sure $PATH gets set up
source ~/.bashrc

cd /Users/yoachim/gitRepos/AstroHireNetwork/doc/tex

# if the .tex file has been edited in the last day
if test `find writeup.tex -mmin -1440`
then
    pdflatex writeup
    bibtex writeup
    pdflatex writeup
    pdflatex writeup
    cp writeup.pdf /Users/yoachim/www/Share/Daily_build/.
    web_up
fi
