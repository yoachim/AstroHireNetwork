#!/bin/sh
# Combine all the data files together

echo 'phd aff; latest year; latest aff; latest 1st year; latest 1st aff; largest publication gap; numRecords; numLinked; uniqueName; latest year unlinked; noAstroJournal; nonUS' > output/all_years.dat

ls output/1*.dat | xargs -I'{}' tail -n +2 '{}' >>  output/all_years.dat
ls output/2*.dat | xargs -I'{}' tail -n +2 '{}' >>  output/all_years.dat
# remove any duplicate lines that snuck in
awk '!seen[$0]++' output/all_years.dat > tmp && mv tmp output/all_years.dat
