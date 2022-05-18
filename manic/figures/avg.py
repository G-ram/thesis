import os
import json
import pprint
import argparse

def pretty_print(data):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)

def set(d, k, v):
	pattern = k.split('.')
	handle = d
	found = False
	i = 0
	idx = 0

	for i, key in enumerate(pattern[:-1]):
		if key in handle:
			idx = i + 1
			found = True
			handle = handle[key]
		else:
			break

	for key in pattern[idx:-1]:
		handle[key] = {}
		handle = handle[key]

	handle[pattern[-1]] = v

def get(data, pattern):
	pattern = pattern.split('.')
	cur_idx = data
	found = True
	for key in pattern:
		if key.startswith('[') and type(cur_idx) is list:
			cur_idx = cur_idx[int(key[1:-1])]
		elif key in cur_idx:
			cur_idx = cur_idx[key]
		else:
			found = False
			break

	return found, cur_idx if found else None

def main(args):
	with open(args.cfg, 'r') as f:
		cfg = json.load(f)

	results = {}
	for obj in cfg:
		with open(obj['src'], 'r') as f:
			data = json.load(f)
			avg = 0
			count = 0
			for key in obj['keys']: 
				found, value = get(data, key['key'])
				if not found:
					print('Not found %s', key['key'])
					return

				normalize = 1
				if 'normalize' in key:
					found, normalize = get(data, key['normalize'])
					if not found:
						print('Not found %s', key['normalize'])
						return

				avg += value / normalize
				count += 1

			set(results, obj['output'], avg / count)

	pretty_print(results)

	if args.dest:
		with open(args.dest, 'w+') as f:
			json.dump(results, f)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dest', type=str, help='Destination')
	parser.add_argument('--cfg', type=str, help='Configuration')
	args = parser.parse_args()
	main(args)