import os
import argparse
import pickle
import json
import numpy as np
use_scipy_spatial = True
try:
	from scipy.spatial import ConvexHull
except:
	print('Scipy spatial not installed')
	use_scipy_spatial = False
# import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.style as style
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import pylab

style.use('bmh')
plt.figure()
stylecolors = [next(plt.gca()._get_lines.prop_cycler)['color'] for i in range(10)]
categories = {'both': stylecolors[0],
				'separate_only': stylecolors[1],
				'prune_only': stylecolors[4],
				'orig': 'k',
				'feasible': '#99cc99', # stylecolors[3],
				'infeasible': '#aaaaaa',
				'oracle': stylecolors[2]}
plt.close('all')
target_network = None

def eq_dict(dict1, dict2):
	if len(set(dict1.keys()) - set(dict2.keys())) != 0: return False
	truth = True
	for k in dict1:
		if type(dict1) != type(dict2): return False
		if type(dict1[k]) is dict: 
			truth &= eq_dict(dict1[k], dict2[k])
		elif dict1[k] != dict2[k]: truth = False

	return truth

def diff(configs1, configs2):
	return set(configs1) - set(configs2)

def flatten(configs, key):
	return [l.stats[key] for l in configs]

def find_pareto_configs(configs, x_key, y_key):
	if len(configs) == 0: return []
	global target_network
	idxs = [x for x in range(len(configs))]
	vals = list(zip(configs, idxs))
	vals.sort(key=lambda x: x[0].stats[x_key])
	pareto_pts = [configs[vals[0][1]]]
	cur_max = configs[vals[0][1]].stats[y_key]
	for _, idx in vals[1:]:
		correction = 0
		if 1: 
			correction = (configs[idx].stats[x_key] / 1e9) ** 2
			if target_network == 'har':
				correction = (configs[idx].stats[x_key] / 7e6) ** 2
			if configs[idx].stats[x_key] == 223365:
				pareto_pts.append(configs[idx])
				# cur_max = configs[idx].stats[y_key]
				continue
		if(configs[idx].stats[y_key] + correction > cur_max):
			if target_network == 'har' and configs[idx].stats[x_key] != 1067798 and configs[idx].stats[x_key] > 1e6:
				continue
			pareto_pts.append(configs[idx])
			cur_max = configs[idx].stats[y_key]

	return pareto_pts

def find_projected_convex_hull(configs, x_key, y_key, c_key='score', buckets=20):
	return find_convex_hull_configs(configs, x_key, c_key)

def find_projected_pareto(configs, x_key, y_key, c_key='acc', buckets=20):
	pareto_pts = find_pareto_configs(configs, x_key, c_key)
	pareto_pts.sort(key=lambda x: x.stats[x_key])
	return pareto_pts

def find_convex_hull_configs(configs, x_key, y_key, buckets=20):
	if len(configs) < 3: return []
	idxs = np.array([x for x in range(0, len(configs))])
	xs = [x.stats[x_key] for x in configs]
	ys = [x.stats[y_key] for x in configs]
	pts = np.column_stack((xs,ys))
	hull = ConvexHull(pts)
	convex_hull_pts = []
	cur_x = 0
	for idx in idxs[hull.vertices][::-1]:
		if(configs[idx].stats[x_key] > cur_x):
			convex_hull_pts.append(configs[idx])
			cur_x = configs[idx].stats[x_key]
	return convex_hull_pts

def filter(configs, comparator):
	return [c for c in configs if comparator(c)]

def check_threshold(config):
	for layer in config.config:
		if config.config[layer]['threshold'] > 0:
			return True

	return False

def check_rank(config, default):
	for layer in config.config:
		if config.config[layer]['rank'] != default.config[layer]['rank']:
			return True

	return False

P_INTERESTING = 0.05
E_SENSE = 10e-3
V_ON = 1.233
V_OFF = 0.9952
COMM_CAP_SIZE = 900e-3
COMM_PACKET_SIZE = 8
E_COMM_PACKET = 0.5 * COMM_CAP_SIZE * (V_ON ** 2 - V_OFF ** 2)

INFER_CAP_SIZE = 1e-3
INFER_OPS = 6e5
INFER_DISCHARGES = 100
E_INFER_SINGLE = 0.5 * INFER_CAP_SIZE * (V_ON ** 2 - V_OFF ** 2)
E_INFER_SCALING =  INFER_DISCHARGES / INFER_OPS

def score(ops, pos, neg, input):
	comm_data_size = input
	e_comm_data = E_COMM_PACKET * comm_data_size / float(COMM_PACKET_SIZE)
	ops_energy = E_INFER_SCALING * ops * E_INFER_SINGLE
	score = P_INTERESTING * pos
	denom = (P_INTERESTING * pos + (1 - P_INTERESTING) * (1 - neg))
	denom *= e_comm_data
	denom += E_SENSE + ops_energy
	score /= denom
	return score

def convert_energy(ops):
	return E_INFER_SCALING * np.array(ops) * E_INFER_SINGLE

def convert_nothing(ops):
	return ops

def plot(configs, root, best, y_key, y_label, convex_hull=False, oracle=False, energy=False):
	fig = plt.figure(figsize=(4,2.75))
	ax = fig.add_subplot(111)
	boundary_pt_fxn = find_pareto_configs
	if convex_hull:
		boundary_pt_fxn = find_projected_pareto # find_convex_hull_configs
	x_transform = convert_nothing
	if energy:
		x_transform = convert_energy
	default = [root]
	best = [best]
	remaining = diff(configs, default)
	ymax = max(flatten(remaining, y_key))

	infeasible = filter(remaining, lambda x: (x.stats['mem'] / 1024 + 60) > 256)
	remaining = diff(remaining, infeasible)
	both = boundary_pt_fxn(filter(remaining, 
		lambda x: check_rank(x, default[0]) and check_threshold(x)), 'ops', y_key)
	remaining = diff(remaining, both)
	prune_only = boundary_pt_fxn(filter(remaining, 
		lambda x: check_threshold(x) and not check_rank(x, default[0])), 'ops', y_key)
	separate_only = boundary_pt_fxn(filter(remaining, 
		lambda x: check_rank(x, default[0]) and not check_threshold(x)), 'ops', y_key)
	remaining = diff(remaining, prune_only)
	remaining = diff(remaining, separate_only)
	ax.plot(x_transform(flatten(infeasible, 'ops')), flatten(infeasible, y_key), 
		c=categories['infeasible'], markersize=5, ls='none', marker='x', alpha=0.5)
	ax.plot(x_transform(flatten(remaining, 'ops')), flatten(remaining, y_key), 
		c=categories['feasible'], markersize=5, ls='none', marker='.', alpha=0.5)
	ax.plot(x_transform(flatten(separate_only, 'ops')), flatten(separate_only, y_key), 
		c=categories['separate_only'], alpha=1, marker='.', markersize=5)
	ax.plot(x_transform(flatten(prune_only, 'ops')), flatten(prune_only, y_key),
		c=categories['prune_only'], alpha=1, marker='.', markersize=5)
	ax.plot(x_transform(flatten(both, 'ops')), flatten(both, y_key), 
		c=categories['both'], alpha=1, marker='.', markersize=5)
	ax.plot(x_transform(flatten(default, 'ops')), flatten(default, y_key),
		c=categories['orig'], marker='x', markersize=10)
	ax.plot(x_transform(flatten(best, 'ops')), flatten(best, y_key),
		c=categories['both'], marker='x', markersize=10)
	if oracle:
		ops = np.linspace(0, np.amax(flatten(remaining, 'ops')), 101)
		ax.plot(x_transform(ops), 1e3 * score(ops, 1, 1, root.stats['input']), c=categories['oracle'], ls='--')
	if energy:
		ax.set_xlabel('Energy per inference (J)')
	else:
		ax.set_xlabel('Multiply-accumulate (MAC) ops')
	ax.ticklabel_format(axis='x', style='sci', scilimits=(-1,1))
	ax.set_ylabel(y_label, fontsize=11)
	ax.set_ylim(0, 1.15 * ymax)
	fig.tight_layout()
	return fig

class Result(object):
	def __init__(self, config, stats):
		self.config = config
		self.stats = stats

	def __str__(self):
		return str({'config': self.config, 'stats': self.stats})

	def __hash__(self):
		return 0

def main(args):
	with open(args.result, 'rb') as f:
		best_result, default, results = pickle.load(f, encoding="latin1")

	global target_network
	if 'har' in args.result: target_network = 'har'
	# for r in results:
		# r.stats['score'] = score(r.stats['ops'], r.stats['acc'], r.stats['acc'], r.stats['input']) * 1000
	# default = Result(default_config, default_result)
	fig = plot(results, default, best_result, 'acc', 'Accuracy')
	if args.dest:
		fig.savefig(args.dest + '.pdf', bbox_inches='tight')

	fig = plot(results, default, best_result, 'score', 
		'Interesting messages sent\nper Joule harvested (IMpJ)', 
		convex_hull=use_scipy_spatial, oracle=False, energy=True)
	if args.dest:
		fig.savefig(args.dest + '_perf.pdf', bbox_inches='tight')
	if args.legend:
		fig = plt.figure(figsize=(1,1))
		legfig = pylab.figure(figsize=(16,2))
		fig.gca().plot([0], color=categories['both'], label='Pareto optimal, Separate + Prune', ls='-', marker='.')
		fig.gca().plot([0], color=categories['separate_only'], label='Pareto optimal, Separate only', ls='-', marker='.')
		fig.gca().plot([0], color=categories['prune_only'], label='Pareto optimal, Prune only', ls='-', marker='.')
		fig.gca().plot([0], color=categories['feasible'], label='Non-pareto (feasible)', ls='none', marker='.')
		fig.gca().plot([0], color=categories['infeasible'], label='Non-pareto (infeasible)', ls='none', marker='x')
		fig.gca().plot([0], color=categories['orig'], label='Original, uncompressed', ls='none', marker='x', markersize=8)
		fig.gca().plot([0], color=categories['both'], label='Configuration Used', ls='none', marker='x', markersize=8)
		# fig.gca().plot([0], color=categories['oracle'], label='Oracle', ls='--')
		leg = fig.gca().get_legend_handles_labels()
		legfig.legend(*leg, ncol=4, handletextpad=0.25, columnspacing=1.5)
		legfig.tight_layout()
		legfig.savefig(args.legend, bbox_inches='tight')
	if not args.dest:
		plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--result',
		type=str,
		help='Results directory')
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination prefix')
	parser.add_argument(
		'--legend',
		type=str,
		help='Generate Legene')
	args = parser.parse_args()
	main(args)