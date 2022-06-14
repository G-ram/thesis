PDFS := overview.pdf device.pdf power.pdf \
	future_model.pdf future_model_legend.pdf \
	progress_energy-graph.pdf progress_perf-graph.pdf progress_eff-graph.pdf

PDFDIR := pdf
PNGDIR := png
CFGDIR := cfg
BLDDIR := bld
CROPPEDPNGS := $(addprefix $(PNGDIR)/, $(PDFS:%.pdf=%-crop.png))
CROPPEDPDFS := $(addprefix $(PDFDIR)/, $(PDFS:%.pdf=%-crop.pdf))

.PHONY: all clean

.SECONDARY:

all: $(CROPPEDPDFS)
	@echo "Finished building figures"

clean:
	rm -rf $(BLDDIR)
	rm -rf $(PDFDIR)
	rm -rf $(PNGDIR)

$(PDFDIR)/doc_data.txt: $(PDFDIR)/figures-crop.pdf
	pdftk $(PDFDIR)/figures-crop.pdf burst output $(PDFDIR)/figures_%02d.pdf

$(PNGDIR)/%-crop.png: $(PDFDIR)/%-crop.pdf
	mkdir -p $(PNGDIR)
	pdftoppm $< $(PNGDIR)/$*-crop -png
	mv $(PNGDIR)/$*-crop-1.png $(PNGDIR)/$*-crop.png

$(PDFDIR)/%-crop.pdf: $(PDFDIR)/%.pdf
	pdfcrop $< $@

$(PDFDIR)/figures-crop.pdf: figures.pdf
	mkdir -p $(PDFDIR)
	pdfcrop figures.pdf $(PDFDIR)/figures-crop.pdf

$(PDFDIR)/overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_01.pdf $(PDFDIR)/overview.pdf

$(PDFDIR)/device.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_02.pdf $(PDFDIR)/device.pdf

$(PDFDIR)/power.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_03.pdf $(PDFDIR)/power.pdf

$(PDFDIR)/future_model.pdf $(PDFDIR)/future_model_legend.pdf: model.py camera.json
	mkdir -p $(PDFDIR)
	python3 model.py  --cfg=camera.json --dest=$(PDFDIR)/future_model.pdf \
		--legend=$(PDFDIR)/future_model_legend.pdf

$(PDFDIR)/%-graph.pdf: $(DATA) bar.py %.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$*.json --dest=$(PDFDIR)/$*-graph.pdf 
