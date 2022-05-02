PDFS := intro.pdf motivate.pdf compilation.pdf execute.pdf \
	arch.pdf pe.pdf die.pdf overview.pdf \
	case_dmm_annotated.pdf case_sort_annotated.pdf case_fft_annotated.pdf \
	energy_all_norm-graph.pdf energy_all_norm_legend-graph.pdf \
	perf-graph.pdf perf_all-graph.pdf \
	case_unroll_norm-graph.pdf case_unroll_perf-graph.pdf \
	case_scratch_norm-graph.pdf case_scratch_perf-graph.pdf \
	energy_overall-graph.pdf perf_overall-graph.pdf \
	energy_avg-graph.pdf \
	case_dmm_energy-graph.pdf case_dmm_energy_legend-graph.pdf \
	case_sort_energy-graph.pdf case_fft_energy-graph.pdf \
	sens_size_energy-graph.pdf sens_size_perf-graph.pdf \
	sens_buf_energy-graph.pdf sens_cfg_energy-graph.pdf

PDFDIR := pdf
CFGDIR := cfg
BLDDIR := bld
DATADIR := ../data
PDFS := $(addprefix $(PDFDIR)/, $(PDFS)) figures.pdf
CROPPEDPDFS := $(PDFS:%.pdf=%-crop.pdf)

.PHONY: all clean

all: $(CROPPEDPDFS) pdf/doc_data.txt
	@echo "Finished building figures"

clean:
	rm pdf/doc_data.txt
	rm figures-crop.pdf
	rm -rf $(DATADIR)
	rm -rf $(BLDDIR)
	rm -rf $(PDFDIR)

pdf/doc_data.txt: figures-crop.pdf
	mkdir -p $(PDFDIR)
	pdftk figures-crop.pdf burst output $(PDFDIR)/figures_%02d.pdf

%-crop.pdf: %.pdf
	pdfcrop $< && touch $@

$(BLDDIR)/avg.json: avg.py $(CFGDIR)/overall_avg.json
	mkdir -p $(BLDDIR)
	python3 avg.py --cfg=$(CFGDIR)/overall_avg.json --dest=$(BLDDIR)/avg.json

$(BLDDIR)/sens.json: avg.py $(CFGDIR)/sens_avg.json
	mkdir -p $(BLDDIR)
	python3 avg.py --cfg=$(CFGDIR)/sens_avg.json --dest=$(BLDDIR)/sens.json

$(PDFDIR)/intro.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_13.pdf $(PDFDIR)/intro.pdf

$(PDFDIR)/motivate.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_17.pdf $(PDFDIR)/motivate.pdf

$(PDFDIR)/overview.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_10.pdf $(PDFDIR)/overview.pdf

$(PDFDIR)/execute.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_19.pdf $(PDFDIR)/execute.pdf

$(PDFDIR)/compilation.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_04.pdf $(PDFDIR)/compilation.pdf

$(PDFDIR)/arch.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_05.pdf $(PDFDIR)/arch.pdf

$(PDFDIR)/pe.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_06.pdf $(PDFDIR)/pe.pdf

$(PDFDIR)/die.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_07.pdf $(PDFDIR)/die.pdf

$(PDFDIR)/case_dmm_annotated.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_20.pdf $(PDFDIR)/case_dmm_annotated.pdf

$(PDFDIR)/case_sort_annotated.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_21.pdf $(PDFDIR)/case_sort_annotated.pdf

$(PDFDIR)/case_fft_annotated.pdf: pdf/doc_data.txt
	cp $(PDFDIR)/figures_22.pdf $(PDFDIR)/case_fft_annotated.pdf

$(PDFDIR)/%_avg-graph.pdf: bar.py $(CFGDIR)/%_avg.json $(BLDDIR)/avg.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/$*_avg.json --dest=$@

$(PDFDIR)/energy_all_norm-graph.pdf: bar.py $(CFGDIR)/energy_all_norm.json $(BLDDIR)/avg.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/energy_all_norm.json --dest=$@

$(PDFDIR)/energy_all_norm_legend-graph.pdf: $(PDFDIR)/energy_all_norm-graph.pdf
	python3 bar.py --cfg=$(CFGDIR)/energy_all_norm.json --legend=$@

$(PDFDIR)/sens_%-graph.pdf: bar.py $(CFGDIR)/sens_%.json $(CFGDIR)/sens_avg.json $(BLDDIR)/sens.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/sens_$*.json --dest=$@

$(PDFDIR)/%_overall-graph.pdf: bar.py $(CFGDIR)/%_overall.json $(BLDDIR)/avg.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/$*_overall.json --dest=$@

$(PDFDIR)/%_legend-graph.pdf: bar.py $(CFGDIR)/%.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/$*.json --legend=$@

$(PDFDIR)/%-graph.pdf: bar.py $(CFGDIR)/%.json
	mkdir -p $(PDFDIR)
	python3 bar.py --cfg=$(CFGDIR)/$*.json --dest=$@