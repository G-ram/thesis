PAPERNAME=paper

all : paper.pdf

.PHONY: figures
figures:
	$(MAKE) -C figures

fast : figures
	pdflatex $(PAPERNAME) </dev/null | tail -n 32
	killall -s 1 -r mupdf ; true

paper.pdf : figures
	pdflatex $(PAPERNAME) </dev/null | tail -n 32
	killall -s 1 -r mupdf ; true
	bibtex -min-crossrefs=30000 $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	killall -s 1 -r mupdf ; true

clean :
	$(MAKE) -C figures clean
	rm paper.bbl paper.blg paper.log paper.out paper.pdf