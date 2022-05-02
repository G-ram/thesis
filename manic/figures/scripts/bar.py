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

colors = ['#a50026','#d73027','#f46d43','#fdae61','#fee090',
			'#ffffbf','#e0f3f8','#abd9e9','#74add1','#4575b4',
			'#313695', '#8c6bb1' ,'#88419d','#810f7c','#4d004b']

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

def get_param(cfg, key, default=None):
	found, val = get(cfg, key)
	if not found and default is None:
		print('%s not found in cfg' % key)
		exit(-1)
	elif not found:
		return default

	return val

class ScalarFormatterForceFormat(ScalarFormatter):
	def _set_format(self, vmin=0, vmax=0):
		self.format = "%1.1f"

def main(args):
	if args.cfg is None:
		print('No config provided')
		return

	with open(args.cfg, 'r') as f:
		cfg = json.load(f)

	height = get_param(cfg, 'height', 5)
	width = get_param(cfg, 'width', 5)
	major_spacing = get_param(cfg, 'major_spacing', 0.75)
	minor_spacing = get_param(cfg, 'minor_spacing', 0.75)
	barwidth = get_param(cfg, 'barwidth', 0.5)
	fontsize = get_param(cfg, 'fontsize', 10)
	major_padding = get_param(cfg, 'major_padding', 25)
	minor_padding = get_param(cfg, 'minor_padding', 25)
	minor_rotation = get_param(cfg, 'minor_rotation', 90)
	major_rotation = get_param(cfg, 'major_rotation', 0)
	rect = get_param(cfg, 'rect', [0, 0, 1, 0.98])
	ylabel = get_param(cfg, 'ylabel', '')
	sci_not = get_param(cfg, "sci_not", True)
	subplots = get_param(cfg, "subplots", False)
	edgecolor = get_param(cfg, "edgecolor", -1)
	edgecolor = None if edgecolor else edgecolor
	ncols = len(get_param(cfg, 'srcs')) if subplots else 1

	fig, axes = plt.subplots(1, ncols, figsize=(width, height))
	axes = axes if subplots else [axes]

	labels = []
	minor_ticks = [0.]
	minor_labels = []
	major_ticks = [0.]
	major_labels = []
	subplots_xlims = []
	for group_idx, group in enumerate(get_param(cfg, 'srcs')):
		if type(group) is not list:
			group = [group]

		minor_ticks_len = len(minor_ticks)
		major_tick = 0
		ax = axes[group_idx] if subplots else axes[0]
		subplots_xlims.append((minor_ticks[-1], 0))
		for bar_idx, bar in enumerate(group):
			src = get_param(bar, 'src')
			scale = get_param(bar, 'scale', 1)
			minor_label = get_param(bar, 'label', '')
			stack = get_param(bar, 'stack')

			with open(src, 'r') as f:
				data = json.load(f)

			minor_labels.append(minor_label)
			minor_ticks.append(minor_ticks[-1] + minor_spacing)
			if bar_idx == 0: minor_ticks[-1] += major_spacing
			major_tick += minor_ticks[-1]

			running_height = 0
			stack = get_param(cfg, 'stacks.%s' % stack)
			for key_idx, key in enumerate(get_param(stack, 'keys')):
				label = get_param(stack, "labels")[key_idx]

				d = 0
				if type(key) is list:
					for k in key:
						_, t = get(data, k)
						d += t
				else: 
					_, d = get(data, key)

				# print('	%s(%d): %f' % (str(key), key_idx, d))
				d *= scale
				color = colors[key_idx] if key_idx < len(colors) else 'grey'
				if 'colors' in stack:
					color = get_param(stack, 'colors.[%d]' % key_idx)

				ax.bar(minor_ticks[-1], d, barwidth, running_height, 
						color=color, edgecolor=edgecolor,
						label=label if label not in labels else '_nolegend_')

				running_height += d
				if label not in labels: 
					labels.append(label)

			if 'total' in stack:
				_, total = get(data, get_param(stack, 'total'))
				print('Total(%s): %f' % (src, d))
				total *= scale
				d = total - running_height
				if d < 0: d = 0
				if d < 0.2 * total: continue 

				ax.bar(minor_ticks[-1], d, barwidth, running_height, 
						color='grey', edgecolor=edgecolor,
						label='Remaining' if 'Remaining' not in labels else '_nolegend_')

				if 'Remaining' not in labels and d > 0.02 * total : labels.append('Remaining')

		subplots_xlims[-1] = (subplots_xlims[-1][0], minor_ticks[-1])
		major_labels.append(get_param(cfg, 'major.[%d]' % group_idx, ''))
		major_ticks.append(major_tick / (len(minor_ticks) - minor_ticks_len))

	for i, ax in enumerate(axes):
		ax.tick_params(axis='x', which='minor', labelsize=fontsize, 
			pad=minor_padding, rotation=minor_rotation)
		ax.set_xticks([tick + 0.001 for tick in minor_ticks[1:]], minor=True)
		ax.set_xticklabels(minor_labels, minor=True)

		ax.tick_params(axis='x', which='major', labelsize=fontsize, 
			pad=major_padding, rotation=major_rotation, bottom=False)
		ax.set_xticks(major_ticks[1:])
		ax.set_xticklabels(major_labels)
		ax.grid(False, axis='x', which='major')
		minx, maxx = subplots_xlims[i]
		minx += minor_spacing + major_spacing - barwidth # - barwidth / 2
		maxx += major_spacing # - barwidth/2
		if subplots: ax.set_xlim(minx, maxx)

		ax.tick_params(axis='y', which='major', labelsize=fontsize)
		ax.set_ylim((0, max(ax.get_ylim()) * 1.025))
		if sci_not: 
			plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
			ax.yaxis.get_offset_text().set_fontsize(fontsize)
			ax.yaxis.set_major_formatter(ScalarFormatterForceFormat())

	ylabel = ylabel.replace('$mu$', r'$\mu$')
	axes[0].set_ylabel(ylabel, fontsize=fontsize)

	fig.tight_layout(rect=rect, w_pad=0.05)

	if args.legend is not None:
		hdls, lbls = axes[0].get_legend_handles_labels()

		fig_legend = plt.figure(figsize=(len(lbls) + 2, 2))
		fig_legend.legend(hdls, lbls, loc='center', 
			ncol=len(lbls))
				
	if args.dest is not None:
		fig.savefig(args.dest)
		if args.legend is not None:
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
		'--legend',
		type=str,
		help='Legend destination')
	args = parser.parse_args()
	main(args)
