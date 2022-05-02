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
rcParams['text.usetex'] = True
import pylab
style.use('bmh')

def main(args):
	with open(args.src, 'r') as f:
		data = json.load(f)

	optimal = {}
	kill = {}

	xs = []
	for k in data:
		if k == 'sched': continue
		ik = int(k)
		optimal[ik] = int(data[k]['optimal'])
		kill[ik] = int(data[k]['kill'])
		if ik not in xs: xs.append(ik)

	xs.sort()

	max_y = 0
	optimal_ys = []
	kill_ys = []
	for i, x in enumerate(xs):
		optimal_ys.append(optimal[x])
		kill_ys.append(kill[x])
		max_y = max(kill_ys[-1], optimal_ys[-1], max_y)

	yticks = [i for i in range(0, max_y, 4)]
	yticks.append(max_y + max_y % 4)

	fig, ax = plt.subplots(figsize=(6, 4))

	line1 = ax.plot(xs, optimal_ys, 'o-', 
		label=r'Optimizing for Window Size ($\mu$arch-specific)', 
		linewidth=4, ms=10)
	line2 = ax.plot(xs, kill_ys, 'x-', 
		label=r'Optimizing for Kill Distance ($\mu$arch-agnostic)', 
		linewidth=4, ms=10)
	if max_y > 10: ax.set_yticks(yticks)
	else: ax.yaxis.set_major_locator(MaxNLocator(integer=True))

	fontsize = 24
	ax.set_xlabel('Window Size', fontsize=fontsize)
	ax.tick_params(axis='x', which='both', labelsize=fontsize)

	ax.set_ylabel('Register writes', fontsize=fontsize)
	ax.tick_params(axis='y', which='both', labelsize=fontsize)

	hdls, lbls = ax.get_legend_handles_labels()
	fig_legend = plt.figure(figsize=(10, 1))
	fig_legend.legend(hdls, lbls, loc='center', ncol=2)

	fig.tight_layout(rect=[0,0,1,0.95])
	if args.dest:
		fig.savefig(args.dest)
		fig_legend.savefig(os.path.join(os.path.dirname(args.dest), 'kill_legend.pdf'))
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
	args = parser.parse_args()
	main(args)