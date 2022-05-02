import os
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.style as style
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
style.use('bmh')

def main(args):
	fig, ax = plt.subplots()
	labels = ['MNIST_SVM', 'MNIST', 'HAR_SVM', 'HAR']
	scores = [20.9558855046, 41.7541381505691, 5.41995188486, 46.710799063935845]
	yticks = [0, 0.3, 0.8, 1.1]
	ax.barh(yticks, scores, 0.25, align='center', color='#348ABD')
	ax.set_yticks(yticks)
	ax.set_yticklabels(labels)
	fig.tight_layout()
	if args.dest:
		fig.savefig(args.dest, bbox_inches='tight')
	else:
		plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination prefix')
	args = parser.parse_args()
	main(args)