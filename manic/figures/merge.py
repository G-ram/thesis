import os
import re
import json
import glob
import pprint
import argparse
import subprocess

# python3 merge.py -k logic sram -d 0284/logic 0284/sram

def execute(cmd):
	p = subprocess.Popen(cmd, shell=True,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	return out, err

def mkdir_p(path):
	cmd = 'mkdir -p %s' % os.path.dirname(path)
	return execute(cmd)

def pretty_print(data):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)

def main(args):
	sources = {}
	for dir in args.dirs:
		for f in glob.glob('%s/**/result.json' % dir, recursive=True):
			for k in args.keys:
				rf = re.search(k, f)
				mf = re.sub(k, 'merged', f)
				if rf is not None:
					if mf in sources:
						sources[mf][k] = f
					else:
						sources[mf] = {k : f}
					break

	for s, v in sources.items():
		print(s)
		merged = {}
		for k, f in v.items():
			with open(f, 'r') as f:
				merged[k] = json.load(f)

		mkdir_p(s)
		with open(s, 'w+') as f:
			json.dump(merged, f)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', '--keys', type=str, nargs='+')
	parser.add_argument('-d', '--dirs', type=str, nargs='+',
		help='Source directories')
	args = parser.parse_args()
	main(args)