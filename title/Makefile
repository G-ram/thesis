PAPERNAME=title
TEX=tex

all : title.pdf

fast:
	pdflatex $(PAPERNAME) </dev/null | tail -n 32
	killall -s 1 -r mupdf ; true

title.pdf:
	pdflatex $(PAPERNAME) </dev/null | tail -n 32
	killall -s 1 -r mupdf ; true
	bibtex -min-crossrefs=30000 $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	killall -s 1 -r mupdf ; true

clean :
	find $(TEX) -name "*.aux" | xargs rm -f
	rm -f title.bbl title.blg title.log \
		title.out title.pdf title.aux \
		title.run.xml title.toc title.lof title.lot