# Ricostruisce i documenti a partire dai file .dfw.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python)
LATEX  ?= pdflatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error -file-line-error

# tre passate: servono per indice e riferimenti incrociati
COMPILA = for i in 1 2 3; do \
            $(LATEX) $(LATEXFLAGS) $$f.tex > /dev/null || { tail -40 $$f.log; exit 1; }; \
          done

.PHONY: all estrai verifica figure capitoli pdf verifica-nota nota controlli dist pulisci

all: dist

estrai: extracted/all.json
# dipende dalla cartella, non dai singoli file: alcuni nomi contengono spazi
extracted/all.json: source tools/dfw_extract.py
	$(PYTHON) tools/dfw_extract.py source extracted/all.json > /dev/null

verifica: extracted/verify.json
extracted/verify.json: extracted/all.json tools/verify.py tools/derive2tex.py
	$(PYTHON) tools/verify.py extracted/all.json extracted/verify.json

figure: tools/make_figures.py
	$(PYTHON) tools/make_figures.py figures > /dev/null

capitoli: extracted/all.json extracted/verify.json $(wildcard commento/*.json) tools/build_tex.py tools/derive2tex.py
	$(PYTHON) tools/build_tex.py . > /dev/null

# edizione integrale
pdf: capitoli figure
	cd tex && f=derive2010 && $(COMPILA)

# ogni affermazione numerica della nota, e la coerenza fra le due lingue
verifica-nota:
	$(PYTHON) tools/verifica_nota.py
	$(PYTHON) tools/controlla_testi.py

# nota, nelle due lingue
nota: figure verifica-nota
	cd nota && for f in nota-it note-en; do $(COMPILA); done

controlli: pdf nota
	$(PYTHON) tools/controlla_pdf.py tex/derive2010.pdf --log tex/derive2010.log --pagine 200 300
	$(PYTHON) tools/controlla_pdf.py nota/nota-it.pdf --log nota/nota-it.log --pagine 15 40
	$(PYTHON) tools/controlla_pdf.py nota/note-en.pdf --log nota/note-en.log --pagine 15 40

# i tre PDF con i nomi della release
dist: controlli
	mkdir -p dist
	cp nota/nota-it.pdf dist/quaderni-derive-nota.pdf
	cp nota/note-en.pdf dist/derive-notebooks-note.pdf
	cp tex/derive2010.pdf dist/quaderni-derive-edizione-integrale.pdf
	@ls -lh dist

pulisci:
	rm -f tex/*.aux tex/*.log tex/*.out tex/*.toc
	rm -f nota/*.aux nota/*.log nota/*.out
	rm -rf dist
