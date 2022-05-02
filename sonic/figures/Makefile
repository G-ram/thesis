PDFS := okg_train.pdf mnist_train.pdf har_train.pdf \
		okg_train_perf.pdf mnist_train_perf.pdf har_train_perf.pdf \
		perf_legend.pdf perf2_legend.pdf train_legend.pdf \
		time_break_legend.pdf micro_energy_legend.pdf \
		motivation_images.pdf motivation_results.pdf \
		mnist_zoom.pdf har_zoom.pdf okg_zoom.pdf \
		cont_zoom.pdf 100uf_zoom.pdf \
		tails_zoom.pdf tails_energy.pdf \
		tails_sonic.pdf comp_designs.pdf hardware.pdf \
		micro_energy.pdf time_break.pdf overview.pdf

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

$(PDFDIR)/comp_designs.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_02.pdf $(PDFDIR)/comp_designs.pdf

$(PDFDIR)/tails_sonic.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_03.pdf $(PDFDIR)/tails_sonic.pdf

$(PDFDIR)/hardware.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_04.pdf $(PDFDIR)/hardware.pdf

$(PDFDIR)/overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_13.pdf $(PDFDIR)/overview.pdf

$(PDFDIR)/okg_train.pdf: $(SCRIPTSDIR)/figure_train.py
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_train.py --result=../data/val/okg/results.summary \
		--dest=$(PDFDIR)/okg_train --legend=$(PDFDIR)/train_legend.pdf

$(PDFDIR)/mnist_train.pdf: $(SCRIPTSDIR)/figure_train.py
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_train.py --result=../data/val/mnist/results.summary \
		 --dest=$(PDFDIR)/mnist_train

$(PDFDIR)/har_train.pdf: $(SCRIPTSDIR)/figure_train.py
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_train.py --result=../data/val/har/results.summary \
		--dest=$(PDFDIR)/har_train

$(PDFDIR)/svm_train.pdf: $(SCRIPTSDIR)/figure_svm.py
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_svm.py --dest=$(PDFDIR)/svm_train.pdf

$(PDFDIR)/train_legend.pdf: $(PDFDIR)/okg_train.pdf

$(PDFDIR)/har_zoom.pdf: $(SCRIPTSDIR)/figure_perf.py $(CFGDIR)/har_perf.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_perf.py --config=$(CFGDIR)/har_perf.json \
		--dest=$(PDFDIR)/har_zoom.pdf

$(PDFDIR)/mnist_zoom.pdf: $(SCRIPTSDIR)/figure_perf.py $(CFGDIR)/mnist_perf.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_perf.py --config=$(CFGDIR)/mnist_perf.json  \
		--dest=$(PDFDIR)/mnist_zoom.pdf --legend=$(PDFDIR)/perf_legend.pdf

$(PDFDIR)/okg_zoom.pdf: $(SCRIPTSDIR)/figure_perf.py $(CFGDIR)/okg_perf.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_perf.py --config=$(CFGDIR)/okg_perf.json \
		 --dest=$(PDFDIR)/okg_zoom.pdf

$(PDFDIR)/cont_zoom.pdf: $(SCRIPTSDIR)/figure_perf.py $(CFGDIR)/cont.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_perf.py --config=$(CFGDIR)/cont.json \
		--dest=$(PDFDIR)/cont_zoom.pdf --zoom=0

$(PDFDIR)/100uf_zoom.pdf: $(SCRIPTSDIR)/figure_perf.py $(CFGDIR)/100uf.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_perf.py --config=$(CFGDIR)/100uf.json  \
		--dest=$(PDFDIR)/100uf_zoom.pdf --zoom=0

$(PDFDIR)/perf_legend.pdf: $(PDFDIR)/mnist_zoom.pdf

$(PDFDIR)/perf2_legend.pdf: $(PDFDIR)/tails_zoom.pdf

$(PDFDIR)/micro_energy_legend.pdf: $(PDFDIR)/micro_energy.pdf

$(PDFDIR)/time_break_legend.pdf: $(PDFDIR)/time_break.pdf

$(PDFDIR)/tails_zoom.pdf: $(SCRIPTSDIR)/figure_perf.py $(CFGDIR)/sensitivity.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_perf.py --config=$(CFGDIR)/sensitivity.json \
		--dest=$(PDFDIR)/tails_zoom.pdf --spacing=2.5 \
		--clegend=$(PDFDIR)/perf2_legend.pdf

$(PDFDIR)/tails_energy.pdf: $(SCRIPTSDIR)/figure_energy.py $(CFGDIR)/energy.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_energy.py \
		--config=$(CFGDIR)/energy.json --dest=$(PDFDIR)/tails_energy.pdf

$(PDFDIR)/motivation_results.pdf : $(SCRIPTSDIR)/motivation.py
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/motivation.py --dest=$(PDFDIR)/motivation

$(PDFDIR)/motivation_images.pdf: $(PDFDIR)/motivation_results.pdf

$(PDFDIR)/micro_energy.pdf: $(SCRIPTSDIR)/figure_prof.py $(CFGDIR)/prof.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_prof.py --config=$(CFGDIR)/prof.json \
		--dest=$(PDFDIR)/micro_energy.pdf --legend=$(PDFDIR)/micro_energy_legend.pdf

$(PDFDIR)/time_break.pdf: $(SCRIPTSDIR)/figure_mac.py $(CFGDIR)/mac.json
	mkdir -p $(PDFDIR)
	python3 $(SCRIPTSDIR)/figure_mac.py --config=$(CFGDIR)/mac.json \
		--dest=$(PDFDIR)/time_break.pdf --legend=$(PDFDIR)/time_break_legend.pdf

%_perf.pdf: %.pdf
	# Do nothing
