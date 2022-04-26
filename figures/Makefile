PDFS := 

PDFDIR := pdf
PNGDIR := png
CFGDIR := cfg
BLDDIR := bld
DATADIR := ../data
CROPPEDPNGS := $(addprefix $(PNGDIR)/, $(PDFS:%.pdf=%-crop.png))
CROPPEDPDFS := $(addprefix $(PDFDIR)/, $(PDFS:%.pdf=%-crop.pdf))

DATA := $(shell find $(DATADIR) -name "*.json")
AVG = $(BLDDIR)/avg_scalar.json $(BLDDIR)/avg_riptide.json

.PHONY: all clean

.SECONDARY:

all: $(CROPPEDPDFS)
	@echo "Finished building figures"

clean:
	rm -rf $(BLDDIR)
	rm -rf $(PDFDIR)
	rm -rf $(PNGDIR)

$(PDFDIR)/doc_data.txt: $(PDFDIR)/figures-crop.pdf
	pdftk figures-crop.pdf burst output $(PDFDIR)/figures_%02d.pdf

$(PNGDIR)/%-crop.png: $(PDFDIR)/%-crop.pdf
	mkdir -p $(PNGDIR)
	pdftoppm $< $(PNGDIR)/$*-crop -png
	mv $(PNGDIR)/$*-crop-1.png $(PNGDIR)/$*-crop.png

$(PDFDIR)/%-crop.pdf: $(PDFDIR)/%.pdf
	pdfcrop $< $@

$(PDFDIR)/figures-crop.pdf: figures.pdf
	mkdir -p $(PDFDIR)
	pdfcrop figures.pdf $(PDFDIR)/figures-crop.pdf

# $(PDFDIR)/overview.pdf: pdf/doc_data.txt
# 	cp $(PDFDIR)/figures_01.pdf $(PDFDIR)/overview.pdf

# $(BLDDIR)/avg_%.json: $(CFGDIR)/avg_%.json
# 	mkdir -p $(BLDDIR)
# 	python3 avg.py --cfg=$(CFGDIR)/avg_$*.json --dest=$(BLDDIR)/avg_$*.json

# $(PDFDIR)/%-graph.pdf $(PDFDIR)/%_legend-graph.pdf: $(DATA) bar.py \
# 	$(CFGDIR)/%.json $(AVG)
# 	mkdir -p $(PDFDIR)
# 	python3 bar.py --cfg=$(CFGDIR)/$*.json --dest=$(PDFDIR)/$*-graph.pdf \
# 		--legend=$(PDFDIR)/$*_legend-graph.pdf
