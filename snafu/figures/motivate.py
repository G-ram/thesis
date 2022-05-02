import argparse
import math
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
	print('no display found. Using non-interactive Agg backend')
	mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.patches as patches
from matplotlib.ticker import ScalarFormatter
plt.rc('text', usetex=True)
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
style.use('bmh')

data = {
	'panic' : 0.5,
	# 'manic' : 0.5,
	# 'msp430' : 3,
	# 'elm' : 28,
	'cma': 11,
	'ulp_srp': 22,
	'hycube' : 70,
	'dsagen' : 105,
	'softbrain' : 119.3,
	'stich' : 140,
	'revel' : 160,
	'plasticine' : 25000,
	'sgmf': 30000
}

lmap = {
	'panic' : 'SNAFU',
	# 'manic' : 'MANIC*',
	# 'msp430' : 'MSP430',
	# 'elm' : 'ELM',
	'cma': 'CMA',
	'ulp_srp': 'ULP-SRP',
	'hycube' : 'HyCube',
	'dsagen' : 'DSAGen',
	'softbrain' : 'Softbrain',
	'stich' : 'Stitch',
	'revel' : 'Revel',
	'plasticine' : 'Plasticine',
	'sgmf' : 'SGMF'
}

def main(args):
	labels = []
	ticks = []
	fig = plt.figure(figsize=(6,3))
	for i, k in enumerate(data):
		v = data[k]
		plt.bar(i, v, color='#41b6c4')
		labels.append(k)
		ticks.append(i)

	labels = [lmap[k] for k in labels]
	plt.xticks(ticks, labels, rotation=90)
	plt.yscale('log')
	plt.ylabel('$\mathbf{Log\:power\:(mW)}$')
	plt.tight_layout(rect=[0, 0, 1, 0.98], w_pad=0.05)

	if args.dest:
		plt.savefig(args.dest)
	elif args.show:
		plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination')
	parser.add_argument(
		'--show',
		action='store_true',
		help='Show graph')
	args = parser.parse_args()
	main(args)