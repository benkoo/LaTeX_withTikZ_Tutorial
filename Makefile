TEX=pdflatex
BIBTEX=bibtex
MAIN=main

TEXSRC=$(wildcard *.tex sections/*.tex figures/*.tex)
PDF=$(MAIN).pdf

all: $(PDF)

# Define the source Markdown file
MD_SOURCE=../wip/experiments/GASing_Arithemtic.md

$(PDF): $(TEXSRC) .author_info.tex bibliography.bib
	@echo "Validating Markdown structure..."
	@python3 validate_markdown_structure.py $(MD_SOURCE) --skip-hierarchy-check > /tmp/md_validation.log || (cat /tmp/md_validation.log && exit 1)
	@CLEANED_MD=$$(tail -n 1 /tmp/md_validation.log); \
	echo "Using cleaned Markdown: $$CLEANED_MD"; \
	python3 auto_transcribe_md_to_tex.py $$CLEANED_MD
	python3 auto_increment_version.py
	$(TEX) $(MAIN).tex
	$(BIBTEX) $(MAIN) || true
	$(TEX) $(MAIN).tex
	$(TEX) $(MAIN).tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk $(PDF)