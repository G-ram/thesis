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
from matplotlib.ticker import MaxNLocator
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import pylab
style.use('bmh')

def main(args):
	with open(args.src, 'r') as f:
		data = json.load(f)

	xsize, ysize = map(int, args.size.split(','))
	fig, ax = plt.subplots(figsize=(xsize, ysize))

	histogram = [0] * (max(map(int, data.keys())) + 1)
	for dist in data:
		histogram[int(dist)] = data[dist]
		# ax.bar(xpos, )

	xpos = 0
	xticks = []
	for x, d in enumerate(histogram):
		ax.bar(x, d, 1, color='#a50026')
		if x > 0: xticks.append(x)
		xpos += 0.25

	if len(histogram) < 6:
		xmax = 6
		xticks = []
		for x in range(1, 7):
			xticks.append(x)
	else:
		xmax = 12
		xticks = []
		for x in range(1, 13, 2):
			xticks.append(x)

	fontsize=16
	ax.set_xlim(0.5, xmax)
	ax.set_xticks(xticks)
	ax.tick_params(axis='x', which='both', labelsize=fontsize)
	ax.set_xlabel('Kill distance', fontsize=fontsize)

	ax.tick_params(axis='y', which='both', labelsize=fontsize)
	ax.set_ylabel('Frequency', fontsize=fontsize)

	plt.tight_layout()

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
		'--dest',
		type=str,
		help='Destination prefix')
	parser.add_argument(
		'--size',
		type=str,
		default='6,4',
		help='Size of figure')
	args = parser.parse_args()
	main(args)