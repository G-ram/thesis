PDFS := overview.pdf scalar_overview.pdf vector_overview.pdf manic_overview.pdf vde.pdf \
	block.pdf transform.pdf dmm_miss.pdf smm_miss.pdf \
	sconv_miss.pdf fft_miss.pdf \
	smm_kill.pdf sconv_kill.pdf fft_kill.pdf kill_legend.pdf \
	sconv_kill_distro.pdf smm_kill_distro.pdf fft_kill_distro.pdf \
	fft_bar.pdf sconv_bar.pdf dconv_bar.pdf dmm_bar.pdf dmv_bar.pdf smm_bar.pdf smv_bar.pdf \
	fft1_bar.pdf sconv1_bar.pdf dconv1_bar.pdf dmm1_bar.pdf dmv1_bar.pdf smm1_bar.pdf smv1_bar.pdf \
	cycles_bar.pdf insn_count_bar.pdf power_bar.pdf sonic_bar.pdf overall_bar.pdf \
	dcache_bar.pdf icache_bar.pdf insn_buf_length_bar.pdf vl_bar.pdf \
	bar_legend.pdf manic_bar.pdf


PDFDIR := pdf
PNGDIR := png
CFGDIR := cfg
BLDDIR := bld
SCRIPTSDIR := scripts
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
	cp $(PDFDIR)/figures_10.pdf $(PDFDIR)/overview.pdf

$(PDFDIR)/scalar_overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_04.pdf $(PDFDIR)/scalar_overview.pdf

$(PDFDIR)/vector_overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_05.pdf $(PDFDIR)/vector_overview.pdf

$(PDFDIR)/manic_overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_06.pdf $(PDFDIR)/manic_overview.pdf

$(PDFDIR)/block.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_20.pdf $(PDFDIR)/block.pdf

$(PDFDIR)/transform.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_12.pdf $(PDFDIR)/transform.pdf

$(PDFDIR)/vde.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_09.pdf $(PDFDIR)/vde.pdf

$(PDFDIR)/%_miss.pdf: $(SCRIPTSDIR)/figure_miss.py
	python3 $(SCRIPTSDIR)/figure_miss.py --src=../data/miss/$*.json --dest=$(PDFDIR)/$*_miss.pdf

$(PDFDIR)/%_kill.pdf: $(SCRIPTSDIR)/figure_kill.py ../data/kill/%.json
	python3 $(SCRIPTSDIR)/figure_kill.py --src=../data/kill/$*.json --dest=$(PDFDIR)/$*_kill.pdf

$(PDFDIR)/kill_legend.pdf: $(PDFDIR)/fft_kill.pdf

$(PDFDIR)/%_bar.pdf: $(SCRIPTSDIR)/bar.py $(CFGDIR)/%_graph.json
	python3 $(SCRIPTSDIR)/bar.py --cfg=$(CFGDIR)/$*_graph.json --dest=$(PDFDIR)/$*_bar.pdf

$(PDFDIR)/fft_bar.pdf: $(SCRIPTSDIR)/bar.py $(CFGDIR)/fft_graph.json
	python3 $(SCRIPTSDIR)/bar.py --cfg=$(CFGDIR)/fft_graph.json --legend=$(PDFDIR)/bar_legend.pdf --dest=$(PDFDIR)/fft_bar.pdf

$(PDFDIR)/bar_legend.pdf: $(PDFDIR)/fft_bar.pdf

$(PDFDIR)/fft_kill_distro.pdf: $(SCRIPTSDIR)/figure_kill_distro.py
	python3 scripts/figure_kill_distro.py --src=../data/kill/fft_distro.json --size=4,3 --dest=$(PDFDIR)/fft_kill_distro.pdf

$(PDFDIR)/%_kill_distro.pdf: $(SCRIPTSDIR)/figure_kill_distro.py
	python3 scripts/figure_kill_distro.py --src=../data/kill/$*_distro.json --size=3,3 --dest=$(PDFDIR)/$*_kill_distro.pdf
