PDFS := execute.pdf cf.pdf overview.pdf router.pdf pe.pdf block.pdf \
	filter.pdf compiler.pdf lso.pdf system.pdf \
	energy-graph.pdf energy_legend-graph.pdf perf-graph.pdf counts-graph.pdf \
	counts_legend-graph.pdf insn-graph.pdf fin-graph.pdf \
	energy_avg-graph.pdf perf_avg-graph.pdf lso-graph.pdf \
	loc_avg-graph.pdf loc_avg_legend-graph.pdf \
	loc-graph.pdf loc_legend-graph.pdf

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
	rm figures-crop.pdf

$(PDFDIR)/doc_data.txt: $(PDFDIR)/figures-crop.pdf
	pdftk figures-crop.pdf burst output $(PDFDIR)/figures_%02d.pdf

$(PNGDIR)/%-crop.png: $(PDFDIR)/%-crop.pdf
	mkdir -p $(PNGDIR)
	pdftoppm $< $(PNGDIR)/$*-crop -png
	mv $(PNGDIR)/$*-crop-1.png $(PNGDIR)/$*-crop.png

$(PDFDIR)/%-crop.pdf: $(PDFDIR)/%.pdf
	pdfcrop $< && touch $@

$(PDFDIR)/figures-crop.pdf: figures.pdf
	mkdir -p $(PDFDIR)
	pdfcrop figures.pdf && touch $(PDFDIR)/figures-crop.pdf

$(PDFDIR)/overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_01.pdf $(PDFDIR)/overview.pdf

$(PDFDIR)/execute.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_16.pdf $(PDFDIR)/execute.pdf

$(PDFDIR)/cf.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_13.pdf $(PDFDIR)/cf.pdf

$(PDFDIR)/router.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_06.pdf $(PDFDIR)/router.pdf

$(PDFDIR)/pe.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_07.pdf $(PDFDIR)/pe.pdf

$(PDFDIR)/block.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_08.pdf $(PDFDIR)/block.pdf

$(PDFDIR)/filter.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_14.pdf $(PDFDIR)/filter.pdf

$(PDFDIR)/compiler.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_04.pdf $(PDFDIR)/compiler.pdf

$(PDFDIR)/lso.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_05.pdf $(PDFDIR)/lso.pdf

$(PDFDIR)/system.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_21.pdf $(PDFDIR)/system.pdf

$(BLDDIR)/avg_%.json: $(CFGDIR)/avg_%.json
	mkdir -p $(BLDDIR)
	python3 avg.py --cfg=$(CFGDIR)/avg_$*.json --dest=$(BLDDIR)/avg_$*.json

$(PDFDIR)/%-graph.pdf $(PDFDIR)/%_legend-graph.pdf: $(DATA) bar.py \
	$(CFGDIR)/%.json $(AVG)
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/$*.json --dest=$(PDFDIR)/$*-graph.pdf \
		--legend=$(PDFDIR)/$*_legend-graph.pdf
