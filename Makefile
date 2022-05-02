PAPERNAME=paper
TEX=tex

all : paper.pdf

.PHONY: figures
figures:
	$(MAKE) -C figures
	$(MAKE) -C sonic/figures
	$(MAKE) -C manic/figures
	$(MAKE) -C snafu/figures
	$(MAKE) -C riptide/figures

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
	$(MAKE) -C sonic/figures clean
	$(MAKE) -C manic/figures clean
	$(MAKE) -C snafu/figures clean
	$(MAKE) -C riptide/figures clean
	find $(TEX) -name "*.aux" | xargs rm -f
	rm -f paper.bbl paper.blg paper.log \
		paper.out paper.pdf paper.aux \
		paper.run.xml paper.toc paper.lof paper.lot