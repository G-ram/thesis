import os
import json
import pickle
import argparse
import pprint
import copy
import numpy as np
import csv
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

stylecolors = ['#4472C4', '#ED7D31', '#F0E442', '#348ABD', '#7A68A6', '#467821',
	'#D55E00', '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2']

def reduce_avg(data):
	if len(data) == 0: return 0
	# return sum(data) / float(len(data))
	return np.median(data)

def reduce_avg_dict(data):
	transformed = {}
	for d in data:
		for key in d:
			if key in transformed: transformed[key].append(d[key])
			else: transformed[key] = [d[key]]

	avgs = {}
	for key in transformed:
		avgs[key] = reduce_avg(transformed[key])

	return avgs

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

V_ON = 1.233
V_OFF = 0.9952
CAP_SIZE = 1e-3
SINGLE_CHARGE_ENERGY = 0.5 * CAP_SIZE * (V_ON ** 2 - V_OFF ** 2)
def convert_energy(charges):
	return 1000 * charges * SINGLE_CHARGE_ENERGY

def compute_energy(data):
	for d in data:
		d['avg_trial']['energy'] = convert_energy(d['avg_trial']['charge'])
		for s in d['avg_trial']['sections']:
			s['energy'] = convert_energy(s['charge'])

def compute_trace(data):
	state = {
		'exp': {'in': 0, 'start': 0, 'time': 0},
		'sec': {'in': 0, 'start': 0, 'time': []},
		'prof': {'in': 0, 'start': 0, 'time': {}},
		'charge': {'in': 0}
	}
	avg_trial = {'exp': [], 'sec': [], 'pulse': []}
	sec_correction = 0
	correction = 0
	charge_pulse_width = 0.
	prof_pulse_width = 0.
	for time, exp, sec, charge, prof in data:
		if charge:
			if exp and state['exp']['in'] == 2:
				state['exp']['in'] = 3
				state['exp']['time'] = time - state['exp']['start'] - correction
				# Record information here
				avg_trial['exp'].append(state['exp']['time'])
				avg_trial['pulse'].append(copy.deepcopy(state['prof']['time']))
				for i, s in enumerate(state['sec']['time']):
					if i >= len(avg_trial['sec']):
						avg_trial['sec'].append([state['sec']['time'][i]])
						continue
					avg_trial['sec'][i].append(state['sec']['time'][i])

				correction = 0
				state['sec']['time'] = []
				state['prof']['time'] = {}
			elif not exp and state['exp']['in'] == 1:
				state['exp']['in'] = 2
				state['exp']['start'] = time
			elif not exp and state['exp']['in'] == 3:
				state['exp']['in'] = 0
			elif exp:
				state['exp']['in'] = 1

			if sec and state['sec']['in'] == 2:
				state['sec']['in'] = 3
				start_time, start_prof = state['sec']['start']
				sec_time = time - start_time - sec_correction
				sec_prof = copy.deepcopy(state['prof']['time'])
				for p in state['prof']['time']:
					if p in start_prof:
						sec_prof[p] -= start_prof[p]

				state['sec']['time'].append((sec_time, sec_prof))
				sec_correction = 0
			elif not sec and state['sec']['in'] == 1:
				state['sec']['in'] = 2
				state['sec']['start'] = (time, copy.deepcopy(state['prof']['time']))
			elif not sec and state['sec']['in'] == 3:
				state['sec']['in'] = 0
			elif sec:
				state['sec']['in'] = 1

		if charge and state['charge']['in'] == 1:
			charge_pulse_width = time - charge_pulse_width
			correction += charge_pulse_width
			sec_correction += charge_pulse_width
			state['charge']['in'] = 0
		elif not charge and state['charge']['in'] == 0:
			charge_pulse_width = time
			state['charge']['in'] = 1

		if not charge and state['prof']['in'] == 2:
			state['prof']['in'] = 0
			prof_pulse_width *= 1e6
			prof_pulse_width = round(prof_pulse_width, 0)
			if prof_pulse_width not in state['prof']['time']:
				state['prof']['time'][prof_pulse_width] = time - state['prof']['start']
				continue
			state['prof']['time'][prof_pulse_width] += time - state['prof']['start']
			continue

		if prof and state['prof']['in'] == 2 and charge:
			state['prof']['in'] = 3
			prof_pulse_width *= 1e6
			prof_pulse_width = round(prof_pulse_width, 0)
			if prof_pulse_width not in state['prof']['time']:
				state['prof']['time'][prof_pulse_width] = time - state['prof']['start']
				continue
			state['prof']['time'][prof_pulse_width] += time - state['prof']['start']
		elif not prof and state['prof']['in'] == 1:
			state['prof']['in'] = 2
			state['prof']['start'] = time
			prof_pulse_width = time - prof_pulse_width
			correction += prof_pulse_width
			sec_correction += prof_pulse_width
		elif not prof and state['prof']['in'] == 3:
			state['prof']['in'] = 0
		elif prof and charge:
			state['prof']['in'] = 1
			prof_pulse_width = time

	# Reduce average
	avg_trial['exp'] = reduce_avg(avg_trial['exp'])
	for i in range(0, len(avg_trial['sec'])):
		times = [x for x, _ in avg_trial['sec'][i]]
		pulses = [x for _, x in avg_trial['sec'][i]]
		pulses = reduce_avg_dict(pulses)
		delete_keys = []
		for p in pulses:
			if pulses[p] < 0.01: delete_keys.append(p)

		for key in delete_keys: pulses.pop(key)
		avg_trial['sec'][i] = {'time': reduce_avg(times), 'pulse': pulses}

	avg_trial['pulse'] = reduce_avg_dict(avg_trial['pulse'])
	delete_keys = []
	for p in avg_trial['pulse']:
		if avg_trial['pulse'][p] < 0.01: delete_keys.append(p)

	for key in delete_keys: avg_trial['pulse'].pop(key)

	return avg_trial

def pretty_print(data):
	pp = pprint.PrettyPrinter(depth=7, width=200)
	pp.pprint(data)

def color_variant(hex_color, brightness_offset=1):
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])

def main(args):
	with open(args.config) as f:
		config = json.load(f)

	data = []
	for path in config['src']:
		for file in os.listdir(path):
			with open(os.path.join(path, file), 'rb') as f:
				d = pickle.load(f, encoding="latin1")
				if d['backend'] == 'tile': d['backend'] = 'tile-' + str(d['tile_size'])
				data.append(d)

	data = filter(data, config['filter'])
	for d in data:
		d['trace'] = config['traces'][config['filter']['eid'].index(d['eid'])]
	compute_time(data)
	compute_diff(data)
	compute_avg(data)

	for d in data:
		with open(os.path.join(config['traces_src'], d['trace']), 'r') as f:
			csv_reader = csv.reader(f)
			trace = []
			for l in csv_reader:
				time, exp, sec, charge, prof = l
				time = float(time)
				exp = int(exp)
				sec = int(sec)
				charge = int(charge)
				prof = int(prof)
				trace.append((time, exp, sec, charge, prof))

			d['trace'] = compute_trace(trace)
			delete_keys = []
			new_pulse = {}
			for p in d['trace']['pulse']:
				new_pulse[config['pulse'][str(int(p))]] = d['trace']['pulse'][p]

			d['trace']['pulse'] = new_pulse

			for sec in d['trace']['sec']:
				new_pulse = {}
				for p in sec['pulse']:
					new_pulse[config['pulse'][str(int(p))]] = sec['pulse'][p]

				sec['pulse'] = new_pulse

			print('-' * 20)
			print(d['eid'])
			pretty_print(d['trace'])

	minor_tick = {o : i for i, o in enumerate(config['minor_order'])}
	major_tick = {o : i for i, o in enumerate(config['major_order'])}
	fig, axes = plt.subplots(nrows=2 if args.zoom else 1, ncols=1, figsize=(5,4), sharex=True)
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
		running_height = 0
		color_idx = 0
		for s in d['trace']['sec']:
			if len(d['trace']['sec']) == 2 and color_idx == 1:
				color_idx += 1
			sec_height = running_height
			for p in s['pulse']:
				running_height += s['pulse'][p]

			sec_height = running_height - sec_height
			for ax in axes:
				ax.bar(idx, sec_height,
					bottom=running_height - sec_height,
					width=MAX_WIDTH * 0.9,  
					color=config['colors'][color_idx], hatch='xxx', 
					linewidth=0,
					edgecolor=color_variant(
							config['colors'][color_idx], brightness_offset=-30))
			sec_remaining_height = s['time'] - sec_height
			for ax in axes:
				ax.bar(idx, sec_remaining_height,
						bottom=running_height,
						width=MAX_WIDTH * 0.9, 
						color=color_variant(
							config['colors'][color_idx], brightness_offset=30))
			running_height += sec_remaining_height
			color_idx += 1

		remaining_energy = d['trace']['exp'] - running_height
		for ax in axes:
			ax.bar(idx, remaining_energy,
				bottom=running_height, 
				width=MAX_WIDTH * 0.9, 
				color=config['colors'][color_idx])
		color_idx += 1;
		running_height += remaining_energy
		if d['backend'] == 'flex' or d['backend'] == 'lea':
			livemax = max(livemax, running_height)

	for ax in axes: ax.set_xticks([tick + 0.002 for tick in minor_ticks], minor=True)
	axes[-1].set_xticklabels(minor_labels, minor=True, rotation = 90,ha='center',fontsize=11)

	axes[-1].tick_params(axis='x', which='major', pad=50)
	for ax in axes: ax.set_xticks(major_ticks)
	axes[-1].set_xticklabels(major_labels, ha='center',fontsize=14)
	plt.tight_layout(rect=[0,0,0.975,1])
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

	if args.legend:
		lbls = ['Kernel - Convolution 1',
			'Control - Convolution 1',
			'Kernel - Convolution 2',
			'Control - Convolution 2',
			'Kernel - Fully-Connected',
			'Control - Fully-Connected',
			'Remaining']
		hdls = []
		color_idx = 0
		for i, l in enumerate(lbls):
			color = config['colors'][color_idx]
			if l.startswith('Control -'):
				color = color_variant(config['colors'][color_idx], brightness_offset=30)
			edgecolor = color
			hatch = 'xxx'
			if l.startswith('Kernel'):
				edgecolor = color_variant(config['colors'][color_idx], brightness_offset=-30)

			patch = patches.Patch(label=l, facecolor=color, 
				hatch=hatch, edgecolor=edgecolor, linewidth=0)
			hdls.append(patch)
			if i != 0 and l.startswith('Control -'):
				color_idx += 1

		legfig = pylab.figure(figsize=(8,3))
		legfig.legend(handles=hdls, labels=lbls, 
				loc='center', ncol=1, columnspacing=1.5, handletextpad=0.25)
		legfig.tight_layout()
		if args.dest:
			legfig.savefig(args.legend)

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
		type=bool,
		default=True,
		help='Zoomed version')
	parser.add_argument(
		'--legend',
		type=str,
		help='Generate Legend')
	parser.add_argument(
		'--spacing',
		type=float,
		default=3.5,
		help='Spacing between groups of bars')
	args = parser.parse_args()
	main(args)
