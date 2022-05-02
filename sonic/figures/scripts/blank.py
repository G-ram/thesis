import pickle
import argparse
import os

blank_exp = {'eid': 1, 'backend': 'tile', 'tile_size': '', 'target': '',
	'trials': [{'charge': {'cycles': 0, 'overflow': 0},
			'off': {'overflow': 0, 'time': 0},
			'overall': {'overflow': 0, 'time': 0},
			'sections': []}]}

def main(args):
	blank_exp['backend'] = args.backend
	blank_exp['tile_size'] = args.tile_size
	blank_exp['target'] = args.target
	blank_exp['eid'] = args.eid
	path = os.path.join(args.dest, '%d.result' % args.eid)
	if os.path.exists(path):
		print("file already exists")
		# return
	with open(path, 'w+') as f:
		pickle.dump(blank_exp, f)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--dest',
		type=str,
		help='Directory to store results')
	parser.add_argument(
		'--target',
		type=str,
		help='Network target')
	parser.add_argument(
		'--backend',
		type=str,
		default='base',
		help='Backend')
	parser.add_argument(
		'--tile_size',
		type=int,
		default=0,
		help='Tile Size')
	parser.add_argument(
		'--eid',
		type=int,
		help='Experiment id')
	args = parser.parse_args()
	main(args)