import argparse
import json
import os
import pprint

pp = pprint.PrettyPrinter(depth=6)

def prettyprint(s):
	pp.pprint(s)

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

def set_key(key, val, result):
	pattern = key.split('.')
	handle = result
	last_handle = result
	for stub in pattern:
		if stub not in handle: handle[stub] = {}
		last_handle = handle
		handle = handle[stub]

	last_handle[stub] = val

def main(args):
	if args.cfg is None:
		print('No config provided')
		return

	with open(args.cfg, 'r') as f:
		cfg = json.load(f)

	results = {}

	for avg in cfg:
		normalize = 'normalize' in avg['keys']
		invert = 'invert' in avg and avg['invert']

		src_keys = [avg['keys']['src']]
		normalize_keys = [avg['keys']['normalize']]
		output_keys = [avg['keys']['output']]
		invert_keys = []

		if type(avg['keys']['src']) != type(avg['keys']['normalize']) or \
			type(avg['keys']['output']) != type(avg['keys']['normalize']):
			print('Key types don\'t match')
			return -1

		if type(avg['keys']['src']) is list:
			src_keys = avg['keys']['src']
			normalize_keys = avg['keys']['normalize']
			output_keys = avg['keys']['output']

		if len(src_keys) != len(normalize_keys) or \
			len(src_keys) != len(output_keys):
			print('Key lengths do not match')
			return -1

		if invert:
			invert_keys = [True for _ in range(len(src_keys))]
		elif 'invert' in avg['keys']:
			if type(avg['keys']['invert']) is list:
				invert_keys = avg['keys']['invert']
			else:
				invert_keys = [avg['keys']['invert'] for _ in range(len(src_keys))]
		else:
			invert_keys = [False for _ in range(len(src_keys))]

		for srckey, normkey, outkey, invertkey in \
			zip(src_keys, normalize_keys, output_keys, invert_keys):
			
			running = 0
			count = 0
			power = -1 if invertkey else 1

			for val in avg['vals']:
				if 'normalize' not in val and normalize:
					print('No source supplied for reference value')
					return -1

				with open(val['src']) as f:
					found, num = get(json.load(f), srckey) 
					if not found:
						print('%s not found in %s' % (srckey, val['src']))
						return -1

				if normalize:
					with open(val['normalize']) as f:
						found, denom = get(json.load(f), normkey)
						if not found:
							print('%s not found in %s n' % (srckey, val['normalize']))
							return -1
				else:
					denom = 1

				running += (num / denom) ** power
				count += 1

				# print(outkey, (num / denom) ** power)

			set_key(outkey, running / count, results)

	if args.dest:
		with open(args.dest, 'w+') as f:
			json.dump(results, f)
	else:
		prettyprint(results)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--cfg',
		type=str,
		help='Config JSON file')
	parser.add_argument(
		'--dest',
		type=str,
		help='Destination')
	args = parser.parse_args()
	main(args)