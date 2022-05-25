import argparse
import json
import os
import numpy as np
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
	print('no display found. Using non-interactive Agg backend')
	mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.patches as patches
from matplotlib.ticker import ScalarFormatter
plt.rc('text', usetex=True)
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
style.use('bmh')

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

def get_param(cfg, key, default=None, required=False):
	found, val = get(cfg, key)
	if not found and default is None and required:
		print('%s not found in cfg' % key)
		exit(-1)
	elif not found:
		return default

	return val

def get_range(l, buckets):
	step = (max(l) - min(l)) / buckets
	return np.arange(min(l), max(l) + 1e-7, step)

def seconds2years(s):
	return s / (365 * 24 * 3600)

def seconds2days(s):
	return s / (24 * 3600)

def years2seconds(y):
	return y * (365 * 24 * 3600)

def main(args):
	with open(args.cfg, 'r') as f:
		cfg = json.load(f)

	sensor_power = get_param(cfg, 'sensor_power')
	sensor_freq = get_param(cfg, 'sensor_freq')
	sensor_latency = get_param(cfg, 'sensor_latency')
	compute_freq = get_param(cfg, 'compute_freq')
	compute_multiplier = get_param(cfg, 'compute_multiplier')
	transmit_bandwidth = get_param(cfg, 'transmit_bandwidth')
	transmit_power = get_param(cfg, 'transmit_power')
	transmit_freq = get_param(cfg, 'transmit_freq')
	problem_size = get_param(cfg, 'problem_size')
	buckets = get_param(cfg, 'buckets')	
	energy_budget = get_param(cfg, 'energy_budget')
	lifetime_target = years2seconds(get_param(cfg, 'lifetime_target'))
	riptide_efficiency = get_param(cfg, 'riptide_efficiency')
	scalar_efficiency = get_param(cfg, 'scalar_efficiency')
	ideal_efficiency = get_param(cfg, 'ideal_efficiency')
	sensor_size = get_param(cfg, 'sensor_size')
	summary_multiplier = get_param(cfg, 'summary_multiplier')

	problem_size_range = get_range(problem_size, buckets)
	sensor_freq_range = get_range(sensor_freq, buckets)
	transmit_freq_range = get_range(transmit_freq, buckets)

	transmit_all = {}
	for size in problem_size_range:
		for freq in sensor_freq_range:
			transmit_latency = size / (max(transmit_bandwidth) * 1e6 / 8)
			transmit_energy = transmit_latency * min(transmit_power) * freq
			sensor_energy = sensor_latency * sensor_power * freq
			lifetime = energy_budget / (transmit_energy + sensor_energy)
			if freq not in transmit_all: transmit_all[freq] = []
			transmit_all[freq].append((size, lifetime))

	scalar_discard = {}
	riptide_discard = {}
	ideal_discard = {}
	ideal_summary_discard = {}
	riptide_summary_discard = {}
	for size in problem_size_range:
		for sfreq in sensor_freq_range:
			if sfreq not in scalar_discard: 
				scalar_discard[sfreq] = {}
				riptide_discard[sfreq] = {}
				ideal_discard[sfreq] = {}
				ideal_summary_discard[sfreq] = {}
				riptide_summary_discard[sfreq] = {}

			for tfreq in transmit_freq_range:
				transmit_latency = size / (min(transmit_bandwidth) * 1e6 / 8)
				transmit_summary_latency = transmit_latency * summary_multiplier

				transmit_energy = transmit_latency * max(transmit_power) * tfreq				
				transmit_summary_energy = \
					transmit_summary_latency * max(transmit_power) * tfreq

				sensor_energy = sensor_latency * sensor_power * sfreq
				ops = size * compute_multiplier / 1e9

				scalar_energy = ops / scalar_efficiency * sfreq
				scalar_lifetime = energy_budget / \
					(scalar_energy + transmit_energy + sensor_energy)

				riptide_energy = ops / riptide_efficiency * sfreq
				riptide_lifetime = energy_budget / \
					(riptide_energy + transmit_energy + sensor_energy)

				riptide_summary_lifetime = energy_budget / \
					(riptide_energy + transmit_summary_energy + sensor_energy)

				ideal_energy = ops / ideal_efficiency * sfreq
				ideal_lifetime = energy_budget / \
					(ideal_energy + transmit_energy + sensor_energy)
				ideal_summary_lifetime = energy_budget / \
					(ideal_energy + transmit_summary_energy + sensor_energy)

				# print(round(size, 2), 
				# 	round(tfreq, 2), 
				# 	round(sfreq, 2),
				# 	f'transmit: {transmit_energy:e}',
				# 	f'sensor: {sensor_energy:e}')

				# for name, energy, lifetime in [
				# 	('scale', scalar_energy, scalar_lifetime), 
				# 	('rip', riptide_energy, riptide_lifetime), 
				# 	('rsum', riptide_energy, riptide_summary_lifetime), 
				# 	('ideal', ideal_energy, ideal_lifetime)]:
				# 	('isum', ideal_energy, ideal_summary_lifetime)]:
				# 	print(f'{name}: {energy:e} {seconds2years(lifetime):.2} ', end='')
				# print('')

				if tfreq not in scalar_discard[sfreq]: 
					scalar_discard[sfreq][tfreq] = []
					riptide_discard[sfreq][tfreq] = []
					ideal_discard[sfreq][tfreq] = []
					ideal_summary_discard[sfreq][tfreq] = []
					riptide_summary_discard[sfreq][tfreq] = []

				scalar_discard[sfreq][tfreq].append((size, scalar_lifetime))
				riptide_discard[sfreq][tfreq].append((size, riptide_lifetime))
				riptide_summary_discard[sfreq][tfreq].append((size, riptide_summary_lifetime))
				ideal_discard[sfreq][tfreq].append((size, ideal_lifetime))
				ideal_summary_discard[sfreq][tfreq].append((size, ideal_summary_lifetime))

	# return

	def to_years(l):
		return list(map(seconds2years, l))

	sfreq = min(sensor_freq_range)
	tfreq = min(transmit_freq_range)

	fig = plt.figure(figsize=(6,4))
	plt.ylabel('Lifetime (years)')
	plt.xlabel('Problem size (input bytes)')
	plt.axhline(seconds2years(lifetime_target), color='grey', linestyle='--')
	plt.text(-2000, seconds2years(lifetime_target) + 0.5, 'Target\nlifetime', 
		fontsize=12)
	plt.axvline(sensor_size, color='darkgrey', linestyle='--')
	plt.text(sensor_size + 500, 26, 'QQVGA (160x120)', fontsize=12)
	plt.plot(
		[x for x, _ in transmit_all[sfreq]], 
		[seconds2years(y) for _, y in transmit_all[sfreq]], 
		color='blue', label='Transmit always')
	plt.plot(
		[x for x, _ in scalar_discard[sfreq][tfreq]], 
		[seconds2years(y) for _, y in scalar_discard[sfreq][tfreq]], 
		color='green', label='Scalar')
	plt.plot(
		[x for x, _ in riptide_discard[sfreq][tfreq]], 
		[seconds2years(y) for _, y in riptide_discard[sfreq][tfreq]], 
		color='red', label='RipTide')
	plt.plot(
		[x for x, _ in riptide_summary_discard[sfreq][tfreq]], 
		[seconds2years(y) for _, y in riptide_summary_discard[sfreq][tfreq]], 
		color='darkred', label='RipTide (Summary)')
	plt.plot(
		[x for x, _ in ideal_discard[sfreq][tfreq]], 
		[seconds2years(y) for _, y in ideal_discard[sfreq][tfreq]], 
		color='black', label='Theoretical (10TOPS/W)')
	# plt.plot(
	# 	[x for x, _ in ideal_summary_discard[sfreq][tfreq]], 
	# 	[seconds2years(y) for _, y in ideal_summary_discard[sfreq][tfreq]], 
	# 	color='black')

	hdls, lbls = fig.axes[0].get_legend_handles_labels()
	fig_legend = plt.figure(figsize=(len(lbls) * 2, 2))
	fig_legend.legend(hdls, lbls, loc='center', ncol=3)

	if args.dest:
		fig.savefig(args.dest)
		if args.legend:
			fig_legend.savefig(args.legend)
	else:
		plt.show()

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
	parser.add_argument(
		'--show',
		action='store_true',
		help='Show graph')
	parser.add_argument(
		'--legend',
		type=str,
		help='Legend destination')
	args = parser.parse_args()
	main(args)