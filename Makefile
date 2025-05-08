TEX=pdflatex
BIBTEX=bibtex
MAIN=main

TEXSRC=$(wildcard *.tex sections/*.tex figures/*.tex)
PDF=$(MAIN).pdf

all: $(PDF)

$(PDF): $(TEXSRC) .author_info.tex bibliography.bib
	$(TEX) $(MAIN).tex
	$(BIBTEX) $(MAIN) || true
	$(TEX) $(MAIN).tex
	$(TEX) $(MAIN).tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk $(PDF)