import os
import io
import re
import csv
import json
import pprint
import argparse
import zipfile
import numpy as np
import scipy.integrate as integrate

import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
	print('no display found. Using non-interactive Agg backend')
	mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.patches as patches
from matplotlib.ticker import FormatStrFormatter
plt.rc('text', usetex=True)
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
style.use('bmh')

CORRECTION = 0.95

def pretty_print(data):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)

def set(d, k, v):
	pattern = k.split('.')
	handle = d
	found = False
	i = 0

	for i, key in enumerate(pattern[:-1]):
		if key in handle:
			found = True
			handle = handle[key]
		else:
			break

	if found:
		i += 1

	for key in pattern[i:-1]:
		handle[key] = {}
		handle = handle[key]

	handle[pattern[-1]] = v

def parse_trace(trace):
	data = {}
	ext = os.path.splitext(trace)[1][1:]
	if ext == 'stpm':
		with zipfile.ZipFile(trace, 'r') as zf:
			for fname in zf.namelist():
				if 'rawfile' not in fname: continue
				with zf.open(fname, 'r') as f:
					reader = csv.reader(
						io.TextIOWrapper(f, 'utf-8'), delimiter=';')
					for row in reader:
						time, amps = tuple(map(float, row))
						data[time] = amps
	elif ext == 'straw':
		with open(trace, 'rb') as f:
			raw = bytes(f.read())

		idx = 0
		begin = None
		delta = None 
		while idx < len(raw):
			header = int.from_bytes(raw[idx:idx+2], 'big')
			if header == 0xf0f3:
				metadata = int.from_bytes(raw[idx+2:idx+6], 'big')
				idx += 9
				if begin is None:
					begin = idx
					delta = metadata 
				else:
					delta = metadata - delta
					break

			idx += 1

		delta /= 1000 # 1000 samples
		delta /= 1000 # ms to s
		idx = begin
		time = 0.

		debug = 0

		while idx < len(raw):
			header = int.from_bytes(raw[idx:idx+2], 'big')
			if header == 0xf0f3:
				metadata = int.from_bytes(raw[idx+2:idx+6], 'big')
				idx += 9
			elif header == 0xf0f4:
				break
			else:
				exponent = (header & 0xf000) >> 12
				factor = header & 0x0fff
				current = factor * (16 ** -exponent)
				time += delta
				idx += 2
				data[time - delta] = current
	else:
		print('Unrecognized file extension %s' % ext)
		return None

	return data

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def main(args):
	trace = args.trace
	start = args.start if args.start else 0
	end = args.end if args.end else None

	print('Trace: %s' % trace)

	if args.output:
		print('Output: %s' % args.output)
		with open(args.output, 'r') as f:
			found_start = False
			for line in f.readlines():
				if 'STAMP' not in line:
					continue

				t = re.findall(r'[-+]?\d*\.\d+|\d+', line)[0]
				if not found_start:
					start = float(t)
					found_start = True
					continue

				end = float(t)

	baseline = 0
	if args.baseline:
		baseline = parse_trace(args.baseline) 
		currents = np.array(list(baseline.values()))
		currents = currents[:int(currents.shape[0] * CORRECTION)]
		currents = moving_average(currents, 100)
		baseline = np.mean(currents)

	data = parse_trace(trace)
	if len(data) == 0:
		print('Trace is empty')
		return

	cmp_times = np.array(list(data.keys()))
	cmp_times = cmp_times[:int(cmp_times.shape[0] * CORRECTION)]
	cmp_currents = np.array(list(data.values()))
	cmp_currents = cmp_currents[:int(cmp_currents.shape[0] * CORRECTION)]
	
	if start or end is not None:
		e = max(data.keys()) if end is None else end
		data = {k:v for k,v in data.items() if k >= start and k <= end}

	times = np.array(list(data.keys()))
	times = times[:int(times.shape[0] * CORRECTION)]
	currents = np.array(list(data.values()))
	currents = currents[:int(currents.shape[0] * CORRECTION)]
	currents -= baseline

	currents = moving_average(currents, 100)
	times = times[:currents.shape[0]]

	# nonzero = currents > 0
	# times = times[nonzero]
	# currents = currents[nonzero]

	# mean = np.mean(currents)
	# standard_deviation = np.std(currents)
	# distance_from_mean = abs(currents - mean)
	# max_deviations = 3
	# not_outlier = distance_from_mean < max_deviations * standard_deviation
	# currents = currents[not_outlier]
	# times = times[not_outlier]

	results = {}

	set(results, 'time', np.max(times) - np.min(times))
	set(results, 'count', times.shape[0])
	
	if args.frequency:
		set(results, 'frequency', args.frequency)
		set(results, 'cycles', int(results['time'] * args.frequency * 1e6))
	
	set(results, 'currents.min', np.min(currents))
	set(results, 'currents.max', np.max(currents))
	set(results, 'currents.avg', np.mean(currents))
	set(results, 'currents.std', np.std(currents))

	if args.voltage:
		power = currents * args.voltage
		energy = integrate.simps(power, times)
		set(results, 'voltage', args.voltage)
		set(results, 'power.min', np.min(power))
		set(results, 'power.max', np.max(power))
		set(results, 'power.avg', np.mean(power))
		set(results, 'power.std', np.std(power))
		set(results, 'energy', energy)

	if args.baseline: set(results, 'path.baseline', args.baseline)
	if args.output: set(results, 'path.output', args.output)
	
	set(results, 'path.trace', trace)

	pretty_print(results)

	results_dest = args.dest
	figure_dest = args.dest

	if args.dest and os.path.isdir(args.dest):
		results_dest = os.path.join(args.dest, 'result.json')
		figure_dest = os.path.join(args.dest, 'current.pdf')

	if results_dest:
		with open(results_dest, 'w+') as f:
			json.dump(results, f)

	if args.plot or args.show:
		fig, ax = plt.subplots(1, 1)
		
		ax.plot(cmp_times, cmp_currents, color='b', linewidth=1)
		_, ma = ax.get_ylim()
		
		if start:
			ax.plot([start, start], [0, ma], color='grey', linewidth=1)

		if end is not None:
			ax.plot([end, end], [0, ma] , color='grey', linewidth=1)

		if figure_dest:
			fig.savefig(figure_dest)
		if args.show:
			plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()	
	parser.add_argument('-d', '--dest', type=str, help='Destination')
	parser.add_argument('--show', action='store_true', help='Show')
	parser.add_argument('--plot', action='store_true', help='Plot')
	parser.add_argument('--start', type=float, help='Start time')
	parser.add_argument('--end', type=float, help='End time')
	parser.add_argument('-f', '--frequency', type=float, help='Frequency')
	parser.add_argument('-v', '--voltage', type=float, help='Voltage')
	parser.add_argument('-b', '--baseline', type=str, help='Baseline current trace')
	parser.add_argument('output', type=str, nargs='?', help='Program output')
	parser.add_argument('trace', type=str, help='Program current trace')
	args = parser.parse_args()
	main(args)