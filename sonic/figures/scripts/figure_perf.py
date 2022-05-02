import os
import json
import pickle
import argparse
import pprint
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import pylab
style.use('bmh')

MAX_WIDTH = 0.5
OVERFLOW = 32767
TIME_MULTIPLIER = 0.0001056965965 * 1000

# plt.figure()
# stylecolors = [ next(plt.gca()._get_lines.prop_cycler)['color'] for i in range(10) ]
# plt.close()
stylecolors = ['#4472C4', '#ED7D31', '#AAAAAA', '#348ABD', '#7A68A6', '#467821',
	'#D55E00', '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2']

def reduce_avg(data):
	if len(data) == 0: return 0
	# return sum(data) / float(len(data))
	return np.median(data)

def filter(data, f):
	filtered_data = []
	for d in data:
		add = True
		for cat in f:
			if type(f[cat]) is list:
				if d[cat] not in f[cat]: add = False
			elif d[cat] != f[cat]:
				add = False
		if add: filtered_data.append(d)

	return filtered_data

def compute_time(data):
	for d in data:
		for t in d['trials']:
			if t['sections'] is not None:
				for s in t['sections']:
					s['overall']['ms'] = s['overall']['overflow'] * OVERFLOW
					s['overall']['ms'] += s['overall']['time']
					s['overall']['ms'] *= TIME_MULTIPLIER

					s['off']['ms'] = s['off']['overflow'] * OVERFLOW
					s['off']['ms'] += s['off']['time']
					s['off']['ms'] *= TIME_MULTIPLIER

					s['charge']['cycles'] = s['charge']['cycles']
					s['charge']['cycles'] += s['charge']['overflow'] * OVERFLOW

			t['overall']['ms'] = t['overall']['overflow'] * OVERFLOW
			t['overall']['ms'] += t['overall']['time']
			t['overall']['ms'] *= TIME_MULTIPLIER

			t['off']['ms'] = t['off']['overflow'] * OVERFLOW
			t['off']['ms'] += t['off']['time']
			t['off']['ms'] *= TIME_MULTIPLIER

			t['charge']['cycles'] = t['charge']['cycles'] 
			t['charge']['cycles'] += t['charge']['overflow'] * OVERFLOW

def compute_diff(data):
	for d in data:
		for t in d['trials']:
			diff = t['overall']['ms'] - t['off']['ms']
			if t['sections'] is not None:
				for s in t['sections']:
					s['diff'] = {'ms': s['overall']['ms'] - s['off']['ms']}
					diff -= s['diff']['ms']

			t['diff'] = {'ms': diff}

def compute_avg(data):
	avg_section = {'overall': [], 'off': [], 'diff': [], 'charge':[]}
	for d in data:
		d['avg_trial'] = {'overall': [], 'off': [], 'diff': [],
			'charge':[], 'sections':[]}
		for t in d['trials'][1:]: # Skip first trial
			if t['sections'] is not None:
				for i, s in enumerate(t['sections']):
					if len(d['avg_trial']['sections']) == i:
						d['avg_trial']['sections'].append(copy.deepcopy(avg_section))

					d['avg_trial']['sections'][i]['overall'].append(s['overall']['ms'])
					d['avg_trial']['sections'][i]['off'].append(s['off']['ms'])
					d['avg_trial']['sections'][i]['diff'].append(s['diff']['ms'])
					d['avg_trial']['sections'][i]['charge'].append(s['charge']['cycles'])

			d['avg_trial']['overall'].append(t['overall']['ms'])
			d['avg_trial']['off'].append(t['off']['ms'])
			d['avg_trial']['diff'].append(t['diff']['ms'])
			d['avg_trial']['charge'].append(t['charge']['cycles'])

		d['avg_trial']['overall'] = reduce_avg(d['avg_trial']['overall'])
		d['avg_trial']['off'] = reduce_avg(d['avg_trial']['off'])
		d['avg_trial']['diff'] = reduce_avg(d['avg_trial']['diff'])
		d['avg_trial']['charge'] = reduce_avg(d['avg_trial']['charge'])
		for i, s in enumerate(d['avg_trial']['sections']):
			d['avg_trial']['sections'][i]['overall'] = reduce_avg(
				d['avg_trial']['sections'][i]['overall'])
			d['avg_trial']['sections'][i]['off'] = reduce_avg(
				d['avg_trial']['sections'][i]['off'])
			d['avg_trial']['sections'][i]['diff'] = reduce_avg(
				d['avg_trial']['sections'][i]['diff'])
			d['avg_trial']['sections'][i]['charge'] = reduce_avg(
				d['avg_trial']['sections'][i]['charge'])

def pretty_print(data):
	pp = pprint.PrettyPrinter(depth=7, width=200)
	pp.pprint(data)

def main(args):
	with open(args.config) as f:
		config = json.load(f)

	data = []
	for path in config['src']:
		cap = path.split('/')[-1]
		for file in os.listdir(path):
			with open(os.path.join(path, file), 'rb') as f:
				d = pickle.load(f, encoding="latin1")
				# data.append(d)
				d['cap'] = cap
				if d['cap'] == 'cont': d['trials'] = [d['trials'][1], d['trials'][0]]
				if d['backend'] == 'tile': d['backend'] = 'tile-' + str(d['tile_size'])
				if d['backend'] == 'lea_fir': 
					if d['lea'] == False: d['backend'] = 'lea_firNo'
					elif d['dma'] == 0: d['backend'] = 'lea_firD0'
					elif d['dma'] == 1: d['backend'] = 'lea_firD1'
				data.append(d)

	data = filter(data, config['filter'])
	compute_time(data)
	compute_diff(data)
	compute_avg(data)

	minor_tick = {o : i for i, o in enumerate(config['minor_order'])}
	major_tick = {o : i for i, o in enumerate(config['major_order'])}
	for d in data:
		print_str = config['major_key'] + ': ' + str(d[config['major_key']]) + ', '
		print_str += config['minor_key'] + ': ' + str(d[config['minor_key']]) + ' => ' 
		print_str += str(d['avg_trial'])
		print(print_str)

	fig, axes = plt.subplots(nrows=2 if args.zoom else 1, ncols=1, figsize=(7,5), sharex=True)
	if args.zoom == 0: axes = [axes]
	livemax = 0
	minor_ticks = []
	minor_labels = []
	major_spacing = args.spacing
	major_ticks = [major_spacing * i for i in range(0, len(config['major_order']))]
	major_labels = config['major_label']
	for d in data:
		idx = major_spacing * major_tick[d[config['major_key']]]
		idx += MAX_WIDTH * (minor_tick[d[config['minor_key']]] - len(minor_tick) / 2)
		minor_ticks.append(idx)
		minor_labels.append(
			config['minor_label'][config['minor_order'].index(d[config['minor_key']])])
		print(idx, d[config['minor_key']], d[config['major_key']])
		if d['avg_trial']['overall'] == 0:
			for i, ax in enumerate(axes):
				marker_y_pos = 1
				if len(axes) == 1:
					marker_y_pos = 3
				elif i == 0 and args.zoom:
					marker_y_pos = 3
				ax.plot(idx, marker_y_pos, marker='x', markersize='8', 
					ls='none', color='#CC0000', label='Does not complete')
			continue
		running_height = 0
		color_idx = 0
		for s in d['avg_trial']['sections']:
			if len(d['avg_trial']['sections']) == 2 and color_idx == 1 and len(config['colors']) == 5:
				color_idx += 1
			for ax in axes:
				ax.bar(idx, s['diff'] / 1000,
					bottom=running_height,
					width=MAX_WIDTH * 0.9, 
					color=config['colors'][color_idx])
			running_height += s['diff'] / 1000
			color_idx += 1;

		for ax in axes:
			ax.bar(idx, d['avg_trial']['diff'] / 1000,
				bottom=running_height, 
				width=MAX_WIDTH * 0.9, 
				color=config['colors'][color_idx])
		color_idx += 1;
		running_height += d['avg_trial']['diff'] / 1000
		if args.zoom == 2 and (d['backend'] == 'flex' or d['backend'] == 'lea'):
			livemax = max(livemax, running_height)
		elif args.zoom == 1:
			livemax = max(livemax, running_height)
		for ax in axes:
			ax.bar(idx, d['avg_trial']['off'] / 1000,
				bottom=running_height,
				width=MAX_WIDTH * 0.9, 
				color=config['colors'][color_idx])

	for ax in axes: 
		ax.tick_params(axis='x', which='minor', labelsize=11, rotation=90)
		ax.set_xticks([tick + 0.002 for tick in minor_ticks], minor=True)
		ax.set_xticklabels(minor_labels, minor=True, rotation=90,ha='center',fontsize=11)

	axes[-1].tick_params(axis='x', which='major', pad=60)
	for ax in axes: ax.set_xticks(major_ticks)
	axes[-1].set_xticklabels(major_labels, ha='center',fontsize=14)
	plt.tight_layout(rect=[0,0,0.975,1])
	if args.zoom == 0: 
		_, livemax = axes[-1].get_ylim()
		axes[-1].set_ylim(0, livemax * 1.05)
	if args.zoom:
		fig.subplots_adjust(hspace=0.075)
		axes[1].set_ylim(0, livemax * 1.1)
		# plt.setp(axes[0].get_xticklabels(minor=True), visible=False, fontsize=12)

		# show zoom
		x = axes[0].get_xlim()[1]
		transFigure = fig.transFigure.inverted()
		b0 = transFigure.transform(axes[0].transData.transform((x + 0.01, 0)))
		b1 = transFigure.transform(axes[1].transData.transform((x + 0.01, 0)))
		m0 = transFigure.transform(axes[0].transData.transform((x + 0.2, livemax / 2)))
		m1 = transFigure.transform(axes[1].transData.transform((x + 0.2, livemax / 2)))
		t0 = transFigure.transform(axes[0].transData.transform((x + 0.01, livemax)))
		t1 = transFigure.transform(axes[1].transData.transform((x + 0.01, livemax)))

		fig.patches.extend([patches.FancyArrowPatch(b0,t0,
							arrowstyle='-', color='grey',
							mutation_scale=5,
							connectionstyle='bar,fraction=%s' % (0.02 / (t0[1] - b0[1])),
							transform=fig.transFigure,figure=fig)])
		fig.patches.extend([patches.FancyArrowPatch(b1,t1,
							arrowstyle='-', color='grey',
							mutation_scale=5,
							connectionstyle='bar,fraction=%s' % (0.02 / (t1[1] - b1[1])),
							transform=fig.transFigure,figure=fig)])
		fig.patches.extend([patches.FancyArrowPatch(m0,m1,
							arrowstyle='fancy', color='grey',
							mutation_scale=10,
							shrinkA=3, shrinkB=3,
							connectionstyle='arc3,rad=-0.2',
							transform=fig.transFigure,figure=fig)])

	if args.legend or args.clegend:
		lbls = ['Live - Convolution 1',
				'Live - Convolution 2', 
				'Live - Fully-Connected', 
				'Live - Other', 
				'Dead (Recharging)', 
				'Does not Complete']
		hdls = [patches.Patch(label=lbls[i], color=config['colors'][i]) for i in range(0, 5)]
		x_mark, = plt.plot([],[], color='#C00000', 
			label='Original, uncompressed', ls='none', marker='x', markersize=8)
		hdls.append(x_mark)
		if args.clegend:
			legfig = pylab.figure(figsize=(8,3))
			legfig.legend(handles=hdls, labels=lbls, 
				loc='center', ncol=2, columnspacing=1.5, handletextpad=0.25)
		else:
			legfig = pylab.figure(figsize=(8,3))
			legfig.legend(handles=hdls, labels=lbls, 
				loc='center', ncol=3, columnspacing=1.5, handletextpad=0.25)
		legfig.tight_layout()
		if args.dest:
			if args.legend:
				legfig.savefig(args.legend)
			else: legfig.savefig(args.clegend)

	if args.dest:
		fig.savefig(args.dest)
	else:
		plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--config',
		type=str,
		help='Configuration file')
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination file')
	parser.add_argument(
		'--zoom',
		type=int,
		default=1,
		help='Zoomed version')
	parser.add_argument(
		'--legend',
		type=str,
		help='Generate Legend')
	parser.add_argument(
		'--clegend',
		type=str,
		help='Generate Compressed Legend')
	parser.add_argument(
		'--spacing',
		type=float,
		default=3.5,
		help='Spacing between groups of bars')
	args = parser.parse_args()
	main(args)
