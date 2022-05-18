import os
import re
import glob
import argparse
import subprocess

def get_freq(p):
	points = {}
	freqs = {}
	points['test'] = [(6, 3)]
	freqs['test'] = [45000]

	invs = {}
	periods = {} # ns
	ratios = {}
	apps = list(points.keys())
	sum_delay = 0
	n_datapoints = 0

	for app in apps:
		invs[app] = [(19 + 2 * p[1]) * (2 ** p[0]) for p in points[app]]
		periods[app] = [1e9 / f for f in freqs[app]]
		ratios[app] = [periods[app][i] / invs[app][i] for i in range(len(invs[app]))]
		for ratio in ratios[app]:
			sum_delay += ratio
			n_datapoints += 1

	delay_per_inv = sum_delay / n_datapoints

	invs = (19 + 2 * p[1]) * (2 ** p[0])
	return 1000000/(delay_per_inv * invs)

def execute(cmd):
	p = subprocess.Popen(cmd, shell=True,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	return out, err

def main(args):
	for f in glob.glob('%s/**/*.stdout' % args.source, recursive=True):
		match = re.search(r'V([0-9.]+)', f)
		voltage = float(match.group(1))
		match = re.search(r'clk_tuple_([0-9]+)_([0-9]+)', f)
		clk_major = int(match.group(1))
		clk_minor = int(match.group(2))
		frequency = get_freq((clk_major, clk_minor))
		trace = f[:-6] + 'straw'
		match = re.search(r'.*/V[0-9.]+', f)
		correct = os.path.join(match.group(0), 'normalize.straw')
		baseline = '--baseline=%s' % correct if os.path.exists(correct) else ''
		dest = os.path.dirname(f)
		plot = '--plot' if args.plot else ''
		cmd = 'python3 trace.py %s --voltage=%f --frequency=%f --dest=%s %s %s %s' % (
			plot, voltage, frequency, dest, baseline, f, trace)
		out, err = execute(cmd)

		if 'Trace is empty' in out.decode('utf-8'):
			print('[ERROR] %s is empty' % trace)
			print(cmd)
			# return
		else:
			print('[INFO] %s success' % trace)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--plot', action='store_true', help='Plot')
	parser.add_argument('source', type=str, help='Source')
	args = parser.parse_args()	
	main(args)