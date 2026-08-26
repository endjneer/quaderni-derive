# Ricostruisce il documento a partire dai file .dfw.
PYTHON ?= python
LATEX  ?= pdflatex

.PHONY: all estrai verifica figure capitoli pdf pulisci

all: pdf

estrai: extracted/all.json
extracted/all.json: $(wildcard source/*.dfw) tools/dfw_extract.py
	$(PYTHON) tools/dfw_extract.py source extracted/all.json > /dev/null

verifica: extracted/verify.json
extracted/verify.json: extracted/all.json tools/verify.py tools/derive2tex.py
	$(PYTHON) tools/verify.py extracted/all.json extracted/verify.json

figure: tools/make_figures.py
	$(PYTHON) tools/make_figures.py figures

capitoli: extracted/all.json extracted/verify.json $(wildcard commento/*.json) tools/build_tex.py tools/derive2tex.py
	$(PYTHON) tools/build_tex.py .

pdf: capitoli figure
	cd tex && $(LATEX) -interaction=nonstopmode -file-line-error derive2010.tex > /dev/null
	cd tex && $(LATEX) -interaction=nonstopmode -file-line-error derive2010.tex > /dev/null
	cd tex && $(LATEX) -interaction=nonstopmode -file-line-error derive2010.tex > /dev/null
	@grep -E '^!' tex/derive2010.log || echo "nessun errore LaTeX"
	@ls -lh tex/derive2010.pdf

pulisci:
	rm -f tex/*.aux tex/*.log tex/*.out tex/*.toc
