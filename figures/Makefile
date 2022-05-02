PDFS := 

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
