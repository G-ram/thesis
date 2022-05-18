import os
import re
import glob
import argparse
import numpy as np

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import colors

def get_freq(p):
	points = {}
	freqs = {}
	points['test'] = [(6, 3)]
	freqs['test'] = [45000]

	invs = {}
	periods = {} # ns
	ratios = {}
	apps = list(points.keys())
	sum_delay = 0
	n_datapoints = 0

	for app in apps:
		invs[app] = [(19 + 2 * p[1]) * (2 ** p[0]) for p in points[app]]
		periods[app] = [1e9 / f for f in freqs[app]]
		ratios[app] = [periods[app][i] / invs[app][i] for i in range(len(invs[app]))]
		for ratio in ratios[app]:
			sum_delay += ratio
			n_datapoints += 1

	delay_per_inv = sum_delay / n_datapoints

	invs = (19 + 2 * p[1]) * (2 ** p[0])
	return 1000000 / (delay_per_inv * invs)

def main(args):
	data = {}
	sram_voltages = set()
	logic_voltages = set()
	clks = set()

	for d in os.listdir(args.src):
		dir_regex = r'[A-Z]+([0-9.]+)_[A-Za-z]+([0-9.]+)_[A-Z]+([0-9]+)_([0-9]+)'
		match = re.match(dir_regex, d)
		if match:
			fail = False
			output_path = os.path.join(args.src, d, 'run.stdout')
			if not os.path.exists(output_path):
				fail = True
				print('Not found:', output_path)
			else:
				with open(output_path, 'r') as f:
					raw = f.read()
					if 'FAIL' in raw:
						fail = True

					if '-448 832 0' not in raw: # Quick check of correctness
						# print('FAILED')
						fail = True

			sram_voltage, logic_voltage, clk_major, clk_minor = match.groups()
			sram_voltage = float(sram_voltage)
			logic_voltage = float(logic_voltage)
			clk_major = int(clk_major)
			clk_minor = int(clk_minor)
			clk = (clk_major, clk_minor)

			sram_voltages.add(sram_voltage)
			logic_voltages.add(logic_voltage)
			clks.add(clk)

			if sram_voltage in data:
				if logic_voltage in data[sram_voltage]:
					data[sram_voltage][logic_voltage][clk] = int(not fail)
				else:
					data[sram_voltage][logic_voltage] = {clk: int(not fail)}
			else:
				data[sram_voltage] = {logic_voltage: {clk: int(not fail)}}

	print('SRAM voltages:', sram_voltages)
	print('Logic voltages:', logic_voltages)
	print('Clocks:', clks)

	clks = sorted(list(clks), key=lambda x: get_freq(x))
	sram_voltages = sorted(sram_voltages)
	heat = np.zeros((len(sram_voltages), len(clks)), dtype=np.uint32)	

	for i, sram_voltage in enumerate(sram_voltages):
		for logic_voltage in logic_voltages:
			if sram_voltage != logic_voltage: continue
			voltage = sram_voltage
			for j, clk in enumerate(clks):
				heat[i,j] = data[voltage][voltage][clk]

	heat = heat[::-1]
	print(heat)

	cmap = colors.ListedColormap(['red', 'green'])
	fig, ax = plt.subplots()
	ax.imshow(heat, cmap=cmap)
	ax.set_ylabel('Voltage (V)', fontsize=12)
	ax.set_xlabel('Frequency (MHz)', fontsize=12)
	ax.set_yticks([i for i in range(len(sram_voltages))])
	ax.set_yticklabels(['%.1f' % x for x in sram_voltages[::-1]])
	ax.set_xticks([i for i in range(len(clks))])
	ax.set_xticklabels(['%.1f' % get_freq(x) for x in clks])

	fig.tight_layout()

	if args.dest:
		fig.savefig(args.dest)
	if args.show:
		plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dest',
		type=str, help='Destination')
	parser.add_argument('--show', action='store_true')
	parser.add_argument('--simple', action='store_true')
	parser.add_argument('src', type=str, help='Source directory')
	args = parser.parse_args()
	main(args)
