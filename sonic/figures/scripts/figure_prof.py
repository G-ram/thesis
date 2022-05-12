import os
import json
import pickle
import argparse
import pprint
import copy
import numpy as np
from intelhex import IntelHex
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import pylab
style.use('bmh')

CONTRIBUTION_CUTOFF = 0.0
START_ADDR = 0x40000
MAX_WIDTH = 0.5
OVERFLOW = 32767
TIME_MULTIPLIER = 0.0001056965965 * 1000

stylecolors = [
	'#9f7ccf', '#654f82', '#41b6c4', '#2d808a', '#1b4c52', '#a1dab4',
	'#7ba689', '#066756', '#95B0B5', '#CE9D80', '#88B467', '#842700']

micro_mapping = {
	'f_mul' : 'F_MUL',
	'f_add' : 'F_ADD',
	'mat_get1D' : 'MAT_GET_1D',
	'mat_get2D' : 'MAT_GET_2D',
	'mat_get3D' : 'MAT_GET_3D',
	'mat_set1D' : 'MAT_SET_1D',
	'mat_set2D' : 'MAT_SET_2D',
	'mat_set3D' : 'MAT_SET_3D',
	'st' : 'st',
	'ld' : 'ld',
	'add' : 'add',
	'mul' : 'mul',
	'inc' : 'inc',
	'loop_inc' : 'loop_inc',
	'loop_add' : 'loop_add',
	'correction' : 'Transition'
}

micro_ordering = ['MAT_GET_1D', 'MAT_GET_2D', 'MAT_GET_3D',
				'ld', 'MAT_SET_1D', 'MAT_SET_2D',
				'MAT_SET_3D', 'st', 'add',
				'mul', 'inc', 'F_ADD', 'F_MUL', 'loop_inc', 'loop_add', 'Transition']

sec_name_mapping = {
	'conv1' : 'Conv 1',
	'conv2' : 'Conv 2',
	'fc' : 'FC',
}

sec_order = ['conv1', 'conv2', 'fc']

def convert_mat_get_1d(data, a, m, l, s):
	a['invocs'] += data['invocs']
	a['ops'] += data['ops']
	l['invocs'] += data['invocs']
	l['ops'] += data['ops']

def convert_mat_get_2d(data, a, m, l, s):
	a['invocs'] += 2 * data['invocs']
	a['ops'] += 2 * data['ops']
	m['invocs'] += data['invocs']
	m['ops'] += data['ops']
	l['invocs'] += 2 * data['invocs']
	l['ops'] += 2 * data['ops']

def convert_mat_get_3d(data, a, m, l, s):
	a['invocs'] += 3 * data['invocs']
	a['ops'] += 3 * data['ops']
	m['invocs'] += 2 * data['invocs']
	m['ops'] += 2 * data['ops']
	l['invocs'] += 3 * data['invocs']
	l['ops'] += 3 * data['ops']

def convert_mat_set_1d(data, a, m, l, s):
	a['invocs'] += data['invocs']
	a['ops'] += data['ops']
	l['invocs'] += data['invocs']
	l['ops'] += data['ops']
	s['invocs'] += data['invocs']
	s['ops'] += data['ops']

def convert_mat_set_2d(data, a, m, l, s):
	a['invocs'] += 2 * data['invocs']
	a['ops'] += 2 * data['ops']
	m['invocs'] += data['invocs']
	m['ops'] += data['ops']
	s['invocs'] += data['invocs']
	s['ops'] += data['ops']

def convert_mat_set_3d(data, a, m, l, s):
	a['invocs'] += 3 * data['invocs']
	a['ops'] += 3 * data['ops']
	m['invocs'] += 2 * data['invocs']
	m['ops'] += 2 * data['ops']
	s['invocs'] += data['invocs']
	s['ops'] += data['ops']

def convert_loop_inc(data, a, m , l, s):
	a['invocs'] += data['invocs']
	a['ops'] += data['invocs']
	l['invocs'] += data['invocs']
	l['ops'] += data['ops']
	s['invocs'] += data['invocs']
	s['ops'] += data['ops']

def convert_loop_add(data, a, m , l, s):
	a['invocs'] += data['invocs']
	a['ops'] += data['invocs']
	l['invocs'] += data['invocs']
	l['ops'] += data['ops']
	s['invocs'] += data['invocs']
	s['ops'] += data['ops']

stat_breakdown = {
	'MAT_GET_1D' : convert_mat_get_1d,
	'MAT_GET_2D' : convert_mat_get_2d,
	'MAT_GET_3D' : convert_mat_get_3d,
	'MAT_SET_1D' : convert_mat_set_1d,
	'MAT_SET_2D' : convert_mat_set_2d,
	'MAT_SET_3D' : convert_mat_set_3d,
	'loop_inc' : convert_loop_inc,
	'loop_add' : convert_loop_add
}

micro_color_mapping = {
	'MAT_GET_1D' : '',
	'MAT_GET_2D' : '',
	'MAT_GET_3D' : '',
	'MAT_SET_1D' : '',
	'MAT_SET_2D' : '',
	'MAT_SET_3D' : '',
	'ld' : '#9f7ccf',
	'st' : '#654f82',
	'add' : '#41b6c4',
	'mul' : '#29848f',
	'inc' : '#135d66',
	'F_ADD' : '#a1dab4',
	'F_MUL' : '#78ab89',
	'loop_inc' : '',
	'loop_add' : '',
	'Transition' : '#dba37d'
}

micro_pretty_name = {
	'MAT_GET_1D' : '',
	'MAT_GET_2D' : '',
	'MAT_GET_3D' : '',
	'MAT_SET_1D' : '',
	'MAT_SET_2D' : '',
	'MAT_SET_3D' : '',
	'ld' : 'Load',
	'st' : 'Store',
	'add' : 'Add',
	'mul' : 'Multiply',
	'inc' : 'Increment',
	'F_ADD' : 'Fixed-Point Add',
	'F_MUL' : 'Fixed-Point Multiply',
	'loop_inc' : '',
	'loop_add' : '',
	'Transition' : 'Task-Transition',
	'Remaining' : 'Remaining'
}

def reduce_avg(data):
	if len(data) == 0: return 0
	return sum(data) / float(len(data))
	# return np.median(data)

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

def compute_charges(data):
	for d in data:
		for t in d['trials']:
			if t['sections'] is not None:
				for s in t['sections']:
					s['charge']['cycles'] = s['charge']['cycles']
					s['charge']['cycles'] += s['charge']['overflow'] * OVERFLOW

			t['charge']['cycles'] = t['charge']['cycles'] 
			t['charge']['cycles'] += t['charge']['overflow'] * OVERFLOW

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

					d['avg_trial']['sections'][i]['charge'].append(s['charge']['cycles'])

			d['avg_trial']['charge'].append(t['charge']['cycles'])

		d['avg_trial']['charge'] = reduce_avg(d['avg_trial']['charge'])
		for i, s in enumerate(d['avg_trial']['sections']):
			d['avg_trial']['sections'][i]['charge'] = reduce_avg(
				d['avg_trial']['sections'][i]['charge'])

V_ON = 1.233
V_OFF = 0.9952
CAP_SIZE = 1e-3
SINGLE_CHARGE_ENERGY = 0.5 * CAP_SIZE * (V_ON ** 2 - V_OFF ** 2)
def convert_energy(charges):
	return charges * SINGLE_CHARGE_ENERGY

def compute_energy(data):
	for d in data:
		d['avg_trial']['energy'] = convert_energy(d['avg_trial']['charge'])
		for s in d['avg_trial']['sections']:
			s['energy'] = convert_energy(s['charge'])

def compute_num(data):
	for d in data:
		with open('tmp.hex', 'w+') as f:
			f.write(d['mem'])

		ih = IntelHex("tmp.hex")
		num = []
		for i in range(START_ADDR, START_ADDR + len(ih), 4):
			n = 0
			for j in range(3, -1, -1):
				n += (ih[i + j] << (8 * j))

			if n != 0:
				num.append(n * 50)

		d['num'] = reduce_avg(num)

def compute_bench_energy(data):
	for d in data:
		d['energy'] = (SINGLE_CHARGE_ENERGY / d['num'])

def remove_placeholders(stats):
	for stat in stats:
		delete_keys = []
		for sec in stat['sections']:
			if sec.startswith('place'):
				delete_keys.append(sec)

		for key in delete_keys: stat['sections'].pop(key, None)

def compute_stat_energy(stats, micro, data, breakdown=False):
	accounted_energy = 0.
	for stat in stats:
		if breakdown:
			if 'add' not in stat['overall']:
				stat['overall']['add'] = {'invocs': 0, 'ops': 0}
			add_handle =  stat['overall']['add']
			if 'mul' not in stat['overall']:
				stat['overall']['mul'] = {'invocs': 0, 'ops': 0}
			mul_handle =  stat['overall']['mul']
			if 'ld' not in stat['overall']:
				stat['overall']['ld'] = {'invocs': 0, 'ops': 0}
			ld_handle =  stat['overall']['ld']
			if 'st' not in stat['overall']:
				stat['overall']['st'] = {'invocs': 0, 'ops': 0}
			st_handle =  stat['overall']['st']

			for s in stat['overall']:
				if s in stat_breakdown:
					stat_breakdown[s](stat['overall'][s], 
						add_handle, mul_handle, ld_handle, st_handle)

			for sec in stat['sections']:
				if 'add' not in stat['sections'][sec]['stats']:
					stat['sections'][sec]['stats']['add'] = {'invocs': 0, 'ops': 0}
				add_handle =  stat['sections'][sec]['stats']['add']
				if 'mul' not in stat['sections'][sec]['stats']:
					stat['sections'][sec]['stats']['mul'] = {'invocs': 0, 'ops': 0}
				mul_handle =  stat['sections'][sec]['stats']['mul']
				if 'ld' not in stat['sections'][sec]['stats']:
					stat['sections'][sec]['stats']['ld'] = {'invocs': 0, 'ops': 0}
				ld_handle =  stat['sections'][sec]['stats']['ld']
				if 'st' not in stat['sections'][sec]['stats']:
					stat['sections'][sec]['stats']['st'] = {'invocs': 0, 'ops': 0}
				st_handle =  stat['sections'][sec]['stats']['st']

				for s in stat['sections'][sec]['stats']:
					if s in stat_breakdown and stat['sections'][sec]['stats'][s]['invocs'] > 0:
						stat_breakdown[s](stat['sections'][sec]['stats'][s], 
							add_handle, mul_handle, ld_handle, st_handle)

		delete_keys = []
		accounted_energy = 0
		for s in stat['overall']:
			if s == 'Transition':
				stat['overall'][s]['energy'] = stat['overall'][s]['ops']
				accounted_energy += stat['overall'][s]['energy']
				continue

			if s in stat_breakdown and breakdown:
				delete_keys.append(s)
				continue

			if s not in micro:
				print(s, 'NOT found')
				continue

			stat['overall'][s]['energy'] = (
				micro[s]['energy'] * stat['overall'][s]['ops'])
			accounted_energy += stat['overall'][s]['energy']

		stat['accounted_energy'] = accounted_energy
		for key in delete_keys: stat['overall'].pop(key, None)

		for sec in stat['sections']:
			delete_keys = []
			accounted_energy = 0
			for s in stat['sections'][sec]['stats']:
				if s == 'Transition':
					stat['sections'][sec]['stats'][s]['energy'] = (
						stat['sections'][sec]['stats'][s]['ops'])
					accounted_energy += stat['sections'][sec]['stats'][s]['energy']
					continue

				if s in stat_breakdown and breakdown:
					delete_keys.append(s)
					continue

				if s not in micro:
					print(s, 'NOT found')
					continue

				stat['sections'][sec]['stats'][s]['energy'] = (
					micro[s]['energy'] * stat['sections'][sec]['stats'][s]['ops'])
				accounted_energy += stat['sections'][sec]['stats'][s]['energy']

			for key in delete_keys: stat['sections'][sec]['stats'].pop(key, None)

			stat['sections'][sec]['accounted_energy'] = accounted_energy

		find_trial = filter(data, 
			{'backend': stat['backend'], 'target': stat['target']})
		if len(find_trial) != 1: 
			print('Too many/few trials')
			continue

		find_trial = find_trial[0]
		stat['total_energy'] = find_trial['avg_trial']['energy']
		stat['diff_energy'] = stat['total_energy'] - stat['accounted_energy']
		for sec in stat['sections']:
			stat['sections'][sec]['total_energy'] = (
				find_trial['avg_trial']['sections'][stat['sections'][sec]['idx']]['energy'])
			stat['sections'][sec]['diff_energy'] = (
				stat['sections'][sec]['total_energy'] - stat['sections'][sec]['accounted_energy'])

def pretty_print(data):
	pp = pprint.PrettyPrinter(depth=6, width=140)
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
				d['cap'] = cap
				if d['backend'] == 'tile': d['backend'] = 'tile-' + str(d['tile_size'])
				data.append(d)

	data = filter(data, config['filter'])
	compute_charges(data)
	compute_avg(data)
	compute_energy(data)

	minor_tick = {o : i for i, o in enumerate(config['minor_order'])}
	major_tick = {o : i for i, o in enumerate(config['major_order'])}
	for d in data:
		total_energy = d['avg_trial']['energy']
		print_str = 'target: ' + str(d['target']) + ', '
		print_str += 'backend: ' + str(d['backend']) + ' => ' 
		print_str += str(1000 * d['avg_trial']['energy']) + 'mJ'
		print(print_str)
		for i, s in enumerate(d['avg_trial']['sections']):
			print("	Section: " + str(i) + ': ' + str(s['energy'] * 1000) + 'mJ')

	micro = {}
	for file in os.listdir(config['micro']):
		with open(os.path.join(config['micro'], file), 'rb') as f:
			d = pickle.load(f, encoding="latin1")
			if d['target'] not in micro_mapping: continue
			d = filter([d], config['micro_filter'])
			if len(d) == 0: continue
			compute_num(d)
			compute_bench_energy(d)
			micro[micro_mapping[d[0]['target']]] = d[0]

	print('')
	stats = []
	for path in config['prof']:
		for file in os.listdir(path):
			with open(os.path.join(path, file), 'r') as f:
				d = json.load(f)[0]
				stats.append(d)

	remove_placeholders(stats)
	compute_stat_energy(stats, micro, data, args.primitive)

	for stat in stats:
		print('-' * 40)
		print(stat['target'], '/', stat['backend'])
		for sec in stat['sections']:
			print('-' * 10	)
			coverage = stat['sections'][sec]['accounted_energy'] / stat['sections'][sec]['total_energy']
			print('	%s => account for %fmJ out of %fmJ, coverage %.2f%%' % (sec,
				stat['sections'][sec]['accounted_energy'] * 1000, 
				stat['sections'][sec]['total_energy'] * 1000, coverage * 100))
			for s in stat['sections'][sec]['stats']:
				print('	', s, '=>', stat['sections'][sec]['stats'][s]['energy'] * 1000)
		print('-' * 10)
		for s in stat['overall']:
			print(s, '=>', stat['overall'][s]['energy'] * 1000	)

		print('')
		accounted_energy = stat['accounted_energy'] * 1000
		total_energy = stat['total_energy'] * 1000
		print('Accounted for %fmJ out of %fmJ, coverage: %0.2f%%' % (
			accounted_energy, total_energy, (accounted_energy / total_energy) * 100))

	fig, ax = plt.subplots(figsize=(5,4))
	minor_ticks = []
	minor_labels = []
	major_ticks = []
	major_labels = []
	labels = []
	color_idx = 0
	for stat in stats:
		ticks_used = []
		idx = major_tick[stat['target']]
		idx += MAX_WIDTH * (minor_tick[stat['backend']] - len(minor_tick) / 2)
		secondary_idx = idx - (len(stat['sections']) / 2.) * MAX_WIDTH * 0.3 - (
			(len(stat['sections']) - 1) * 0.05)
		major_labels.append(config['major_label'][config['major_order'].index(stat['target'])])
		print(idx, stat['backend'], stat['target'])
		running_height = 0
		for s in micro_ordering:
			if s not in stat['overall']: continue
			if stat['overall'][s]['energy'] < stat['total_energy'] * CONTRIBUTION_CUTOFF: 
				stat['diff_energy'] += stat['overall'][s]['energy']
				continue
			if s not in micro_color_mapping:
				micro_color_mapping[s] = stylecolors[color_idx]
				color_idx += 1
			ax.bar(secondary_idx, stat['overall'][s]['energy'] * 1000,
				bottom=running_height,
				width=MAX_WIDTH * 0.3,
				label=s if s not in labels else '',
				color=micro_color_mapping[s])
			if s not in labels:
				order = micro_ordering.index(s)
				idx = 0
				for l in labels:
					if l != 'Remaining' and order > micro_ordering.index(l):
						idx += 1
				labels.insert(idx, s)
			running_height += stat['overall'][s]['energy'] * 1000

		ax.bar(secondary_idx, stat['diff_energy'] * 1000,
				bottom=running_height, 
				width=MAX_WIDTH * 0.3, 
				label='Remaining' if 'Remaining' not in labels else '', 
				color='#A7A7A4')
		running_height += stat['diff_energy'] * 1000
		if 'Remaining' not in labels: labels.append('Remaining')
		minor_ticks.append(secondary_idx)
		ticks_used.append(secondary_idx)
		minor_labels.append('Overall')

		for sec in sec_order: 
			if sec not in stat['sections']: continue
			running_height = 0
			secondary_idx += MAX_WIDTH * 0.3 + 0.05
			for s in micro_ordering:
				if s not in stat['sections'][sec]['stats']: continue
				if stat['sections'][sec]['stats'][s]['energy'] < (
					stat['sections'][sec]['accounted_energy'] * CONTRIBUTION_CUTOFF): 
					stat['sections'][sec]['diff_energy'] += (
						stat['sections'][sec]['stats'][s]['energy'])
					continue
				if s not in micro_color_mapping:
					micro_color_mapping[s] = stylecolors[color_idx]
					color_idx += 1
				ax.bar(secondary_idx, stat['sections'][sec]['stats'][s]['energy'] * 1000,
					bottom=running_height,
					width=MAX_WIDTH * 0.3,
					label=s if s not in labels else '',
					color=micro_color_mapping[s])
				if s not in labels:
					order = micro_ordering.index(s)
					idx = 0
					for l in labels:
						if l != 'Remaining' and  order > micro_ordering.index(l):
							idx += 1
					labels.insert(idx, s)
				running_height += stat['sections'][sec]['stats'][s]['energy'] * 1000

			ax.bar(secondary_idx, stat['sections'][sec]['diff_energy'] * 1000,
				bottom=running_height, 
				width=MAX_WIDTH * 0.3, 
				label='Remaining' if 'Remaining' not in labels else '', 
				color='#A7A7A4')
			running_height += stat['sections'][sec]['diff_energy'] * 1000
			minor_ticks.append(secondary_idx)
			minor_labels.append(sec_name_mapping[sec])
			ticks_used.append(secondary_idx)

		major_ticks.append(sum(ticks_used) / len(ticks_used))

	ax.set_xticks([tick + 0.002 for tick in minor_ticks], minor=True)
	ax.set_xticklabels(minor_labels, minor=True, rotation = 90,ha='center',fontsize=11)

	ax.tick_params(axis='x', which='major', pad=50, bottom=False)
	ax.set_xticks(major_ticks)
	ax.set_xticklabels(major_labels, ha='center',fontsize=14)
	plt.tight_layout(rect=[0,0,1,1])
	if args.legend:
		handles, labels_ = ax.get_legend_handles_labels()
		new_idxs = [labels_.index(l) for l in labels]
		labels = [micro_pretty_name[l] for l in labels]
		handles = [handles[i] for i in new_idxs]
		legfig = pylab.figure(figsize=(8,3))
		legfig.legend(handles=handles[::-1], labels=labels[::-1], 
			loc='center', ncol=1, columnspacing=1.5, handletextpad=0.25)
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
		'--primitive',
		type=bool,
		default=True,
		help='Break stats into primitive instructions')
	parser.add_argument(
		'--legend',
		type=str,
		help='Generate Legend')
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination file')
	args = parser.parse_args()
	main(args)
