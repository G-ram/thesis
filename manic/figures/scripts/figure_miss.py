import argparse
import json
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
	print('no display found. Using non-interactive Agg backend')
	mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import pylab
style.use('bmh')

def main(args):
	data_key = 'histogram'
	if args.write: data_key = 'write_histogram'
	positions = []
	heights = []
	with open(args.src, 'r') as f:
		data = json.load(f)
		for key in data[data_key]:
			positions.append(int(key))
			heights.append(data[data_key][key])

	minimum = min(positions)
	maximum = max(positions)
	hist = [0 for i in range(0, maximum + 1)]
	for i, p in enumerate(positions):
		hist[p] = heights[i]

	fig, ax = plt.subplots(figsize=(6, 4))
	running_sum = 0
	running_sums = []
	for freq in hist:
		running_sums.append(running_sum)
		running_sum += freq

	xticks = []
	xlabels = []
	xs = []
	ys = []
	maxy = 0
	for i, ifreq in enumerate(running_sums[0:args.cutoff]):
		diff = running_sum - ifreq
		if args.normalize: diff = float(diff) / running_sum
		if i % 64 == 0:
			b = args.line_size * i
			xlabels.append('%dB' % b if b < 1024 else '%.1fKB' % (float(b) / 1024))
			xticks.append(i)

		xs.append(i)
		ys.append(diff)
		if diff > maxy: maxy = diff

	b = args.line_size * (i + 1)
	xlabels.append('%dB' % b if b < 1024 else '%.1fKB' % (float(b) / 1024))
	xticks.append(i)

	if args.normalize: maxy = 1

	fontsize = 18
	ax.plot(xs, ys, '-', linewidth=5)
	
	ax.tick_params(axis='x', which='both', labelsize=fontsize)
	ax.set_xticks(xticks)
	ax.set_xticklabels(xlabels)
	ax.set_xlabel('Cache Size', fontsize=fontsize)

	ax.set_ylim(0, maxy * 1.1)
	ax.set_ylabel('Number of Misses', fontsize=fontsize)
	ax.tick_params(axis='y', which='both', labelsize=fontsize)
	ax.yaxis.get_offset_text().set_fontsize(fontsize)
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

	plt.tight_layout(rect=[0,0,0.95,0.975])
	if args.dest:
		fig.savefig(args.dest)
	else:
		plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--src',
		type=str,
		help='Source JSON file')
	parser.add_argument(
		'--write',
		action='store_true',
		help='LRU data')
	parser.add_argument(
		'--normalize',
		action='store_true',
		help='Normalize data')
	parser.add_argument(
		'--cutoff',
		type=int,
		default=256,
		help='Cutoff')
	parser.add_argument(
		'--line_size',
		type=int,
		default=8,
		help='Cutoff')
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination prefix')
	args = parser.parse_args()
	main(args)