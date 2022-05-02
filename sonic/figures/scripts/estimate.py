import os
import json
import pickle
import argparse
import pprint
import copy
import numpy as np
from intelhex import IntelHex

CONTRIBUTION_CUTOFF = 0.0
START_ADDR = 0x40000
MAX_WIDTH = 0.5
OVERFLOW = 32767
TIME_MULTIPLIER = 0.0001056965965 * 1000

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
	'correction' : 'Transition',
	'none' : 'None'
}

decode_energy_mapping = {
	'f_mul' : 6,
	'f_add' : 1,
	'st' : 1,
	'ld' : 1,
	'add' : 1,
	'mul' : 4,
	'inc' : 1,
}

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

def compute_bench_energy_no_decode(data, decode_energy=2.1e-9):
	for d in data:
		d['energy_no_decode'] = (SINGLE_CHARGE_ENERGY / d['num']) 
		if d['target'] not in decode_energy_mapping:
			d['energy_no_decode'] -= decode_energy
			continue
		d['energy_no_decode'] -= decode_energy_mapping[d['target']] * decode_energy

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

			stat['overall']['add_idx'] = {'invocs': 0, 'ops': 0}
			stat['overall']['mul_idx'] = {'invocs': 0, 'ops': 0}
			stat['overall']['ld_idx'] = {'invocs': 0, 'ops': 0}
			stat['overall']['st_idx'] = {'invocs': 0, 'ops': 0}
			add_idx_handle = stat['overall']['add_idx']
			mul_idx_handle = stat['overall']['mul_idx']
			ld_idx_handle = stat['overall']['ld_idx']
			st_idx_handle = stat['overall']['st_idx']

			for s in stat['overall']:
				if s in stat_breakdown:
					stat_breakdown[s](stat['overall'][s], 
						add_handle, mul_handle, ld_handle, st_handle)
					if s == 'loop_add' or s == 'loop_inc':
						stat_breakdown[s](stat['overall'][s], 
						add_idx_handle, mul_idx_handle, ld_idx_handle, st_idx_handle)

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
		accounted_energy_no_decode = 0
		for s in stat['overall']:
			if s == 'Transition':
				stat['overall'][s]['energy'] = stat['overall'][s]['ops']
				stat['overall'][s]['energy_no_decode'] = stat['overall'][s]['ops']
				accounted_energy += stat['overall'][s]['energy']
				accounted_energy_no_decode += stat['overall'][s]['energy']
				continue

			if '_idx' in s:
				stat['overall'][s]['energy'] = (
					micro[s[:s.index('_')]]['energy'] * stat['overall'][s]['ops'])
				stat['overall'][s]['energy_no_decode'] = (
					micro[s[:s.index('_')]]['energy_no_decode'] * stat['overall'][s]['ops'])

			if s in stat_breakdown and breakdown:
				delete_keys.append(s)
				continue

			if s not in micro:
				print(s, 'NOT found')
				continue

			stat['overall'][s]['energy'] = (
				micro[s]['energy'] * stat['overall'][s]['ops'])
			accounted_energy += stat['overall'][s]['energy']
			stat['overall'][s]['energy_no_decode'] = (
				micro[s]['energy_no_decode'] * stat['overall'][s]['ops'])
			accounted_energy_no_decode += stat['overall'][s]['energy_no_decode']

		stat['accounted_energy'] = accounted_energy
		stat['accounted_energy_no_decode'] = accounted_energy_no_decode
		for key in delete_keys: stat['overall'].pop(key, None)

		for sec in stat['sections']:
			delete_keys = []
			accounted_energy = 0
			accounted_energy_no_decode = 0
			for s in stat['sections'][sec]['stats']:
				if s == 'Transition':
					stat['sections'][sec]['stats'][s]['energy'] = (
						stat['sections'][sec]['stats'][s]['ops'])
					stat['sections'][sec]['stats'][s]['energy_no_decode'] = (
						stat['sections'][sec]['stats'][s]['ops'])
					accounted_energy += stat['sections'][sec]['stats'][s]['energy']
					accounted_energy_no_decode += stat['sections'][sec]['stats'][s]['energy_no_decode']
					continue

				if s in stat_breakdown and breakdown:
					delete_keys.append(s)
					continue

				if '_idx' in s:
					stat['sections'][sec]['stats'][s]['energy'] = (
					micro[s[:s.index('_')]]['energy'] * stat['sections'][sec]['stats'][s]['ops'])
					stat['sections'][sec]['stats'][s]['energy_no_decode'] = (
						micro[s[:s.index('_')]]['energy_no_decode'] * stat['sections'][sec]['stats'][s]['ops'])
					continue

				if s not in micro:
					print(s, 'NOT found')
					continue

				stat['sections'][sec]['stats'][s]['energy'] = (
					micro[s]['energy'] * stat['sections'][sec]['stats'][s]['ops'])
				accounted_energy += stat['sections'][sec]['stats'][s]['energy']
				stat['sections'][sec]['stats'][s]['energy_no_decode'] = (
					micro[s]['energy_no_decode'] * stat['sections'][sec]['stats'][s]['ops'])
				accounted_energy_no_decode += stat['sections'][sec]['stats'][s]['energy_no_decode']

			for key in delete_keys: stat['sections'][sec]['stats'].pop(key, None)

			stat['sections'][sec]['accounted_energy'] = accounted_energy
			stat['sections'][sec]['accounted_energy_no_decode'] = accounted_energy_no_decode

		find_trial = filter(data, 
			{'backend': stat['backend'], 'target': stat['target']})
		if len(find_trial) != 1: 
			print('Too many/few trials')
			continue

		find_trial = find_trial[0]
		stat['total_energy'] = find_trial['avg_trial']['energy']
		stat['diff_energy'] = stat['total_energy'] - stat['accounted_energy']
		stat['diff_energy_no_decode'] = stat['total_energy'] - stat['accounted_energy_no_decode']
		for sec in stat['sections']:
			stat['sections'][sec]['total_energy'] = (
				find_trial['avg_trial']['sections'][stat['sections'][sec]['idx']]['energy'])
			stat['sections'][sec]['diff_energy'] = (
				stat['sections'][sec]['total_energy'] - stat['sections'][sec]['accounted_energy'])
			stat['sections'][sec]['diff_energy_no_decode'] = (
				stat['sections'][sec]['total_energy'] - stat['sections'][sec]['accounted_energy_no_decode'])

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
			with open(os.path.join(path, file), 'r') as f:
				d = pickle.load(f)
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
		with open(os.path.join(config['micro'], file), 'r') as f:
			d = pickle.load(f)
			if d['target'] not in micro_mapping: continue
			d = filter([d], config['micro_filter'])
			if len(d) == 0: continue
			compute_num(d)
			compute_bench_energy(d)
			micro[micro_mapping[d[0]['target']]] = d[0]

	for m in micro:
		if m == 'None':
			decode_energy = micro[m]['energy']

	for m in micro:
		compute_bench_energy_no_decode([micro[m]], decode_energy)

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
			print('	%s => %fmJ, no decode: %fmJ' % (sec,
				stat['sections'][sec]['accounted_energy'] * 1000, 
				stat['sections'][sec]['accounted_energy_no_decode'] * 1000))
			for s in stat['sections'][sec]['stats']:
				print('	  %s => %fmJ, no decode: %fmJ' % (s,
					stat['sections'][sec]['stats'][s]['energy'] * 1000,
					stat['sections'][sec]['stats'][s]['energy_no_decode'] * 1000))
		print('-' * 10)
		loop_idx_energy = 0
		mem_energy = 0
		loop_idx_energy_no_decode = 0
		mem_energy_no_decode = 0
		for s in stat['overall']:
			print('%s => %fmJ, no decode: %fmJ' % (s, 
				stat['overall'][s]['energy'] * 1000,
				stat['overall'][s]['energy_no_decode'] * 1000))
			if '_idx' in s:
				loop_idx_energy += stat['overall'][s]['energy']
				loop_idx_energy_no_decode += stat['overall'][s]['energy_no_decode']
			if s == 'ld' or s == 'st':
				mem_energy += stat['overall'][s]['energy']
				mem_energy_no_decode += stat['overall'][s]['energy_no_decode']

		print('')
		print('Loop Manipulation energy %fmJ (%.2f%%), no decode: %fmJ (%.2f%%)' % (
			loop_idx_energy * 1000, (loop_idx_energy / mem_energy) * 100, 
			loop_idx_energy_no_decode * 1000, 
			(loop_idx_energy_no_decode / mem_energy_no_decode) * 100))
		print('')
		accounted_energy = stat['accounted_energy'] * 1000
		accounted_energy_no_decode = stat['accounted_energy_no_decode'] * 1000
		total_energy = stat['total_energy'] * 1000
		print('Energy: %fmJ No Decode: %fmJ Total: %fmJ %.2f%% saved' % (
			accounted_energy, accounted_energy_no_decode, total_energy, 
			(1 - (accounted_energy_no_decode / accounted_energy)) * 100))

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
	args = parser.parse_args()
	main(args)
