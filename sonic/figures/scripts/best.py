import os
import json
import pickle
import argparse
import pprint
import copy
import numpy as np

MAX_WIDTH = 0.5
OVERFLOW = 32767
TIME_MULTIPLIER = 0.0001056965965 * 1000

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
                        d['avg_trial']['sections'][i]['overall'] = reduce_avg(d['avg_trial']['sections'][i]['overall'])
                        d['avg_trial']['sections'][i]['off'] = reduce_avg(d['avg_trial']['sections'][i]['off'])
                        d['avg_trial']['sections'][i]['diff'] = reduce_avg(d['avg_trial']['sections'][i]['diff'])
                        d['avg_trial']['sections'][i]['charge'] = reduce_avg(d['avg_trial']['sections'][i]['charge'])

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
			with open(os.path.join(path, file), 'r') as f:
				d = pickle.load(f)
				d['cap'] = cap
				if d['cap'] == 'cont': d['trials'] = [d['trials'][1], d['trials'][0]]
				if d['backend'] == 'tile': d['backend'] = 'tile-' + str(d['tile_size'])
				data.append(d)

	data = filter(data, config['filter'])
	compute_time(data)
	compute_diff(data)
	compute_avg(data)

	base = filter(data, {'eid': config['base']})[0]
	for d in data:
		print('%s (%s) is %.2fx slower than base' % (d['target'], d['backend'],
			d['avg_trial']['overall'] / base['avg_trial']['overall']))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--config',
		type=str,
		help='Configuration file')
	args = parser.parse_args()
	main(args)
