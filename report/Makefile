all: report.pdf

report.pdf: report.md citations.bib
	pandoc --toc --filter pandoc-citeproc --bibliography=citations.bib --variable papersize=a4paper -s -o report.pdf report.md
