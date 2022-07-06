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

class ScalarFormatterForceFormat(ScalarFormatter):
	def _set_format(self, vmin=0, vmax=0):
		self.format = '%1.1f'

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

def main(args):
	if args.cfg is None:
		print('No config provided')
		return

	with open(args.cfg, 'r') as f:
		cfg = json.load(f)

	height = get_param(cfg, 'height', 5)
	width = get_param(cfg, 'width', 5)
	major_spacing = get_param(cfg, 'major_spacing', 0.75)
	supermajor_spacing = get_param(cfg, 'supermajor_spacing', 0)
	supermajor_index = get_param(cfg, 'supermajor_index', 1)
	minor_spacing = get_param(cfg, 'minor_spacing', 0.75)
	barwidth = get_param(cfg, 'barwidth', 0.5)
	fontsize = get_param(cfg, 'fontsize', 10)
	major_padding = get_param(cfg, 'major_padding', 25)
	minor_padding = get_param(cfg, 'minor_padding', 25)
	minor_rotation = get_param(cfg, 'minor_rotation', 90)
	major_rotation = get_param(cfg, 'major_rotation', 0)
	overlay = get_param(cfg, 'overlay', False)
	rect = get_param(cfg, 'rect', [0, 0, 1, 0.98])
	ylabel = get_param(cfg, 'ylabel', '')
	log = get_param(cfg, 'log', False)
	dual_label = get_param(cfg, 'dual_label', '')
	sci_not = get_param(cfg, 'sci_not', True)
	subplots = get_param(cfg, 'subplots', False)
	draw_norm = get_param(cfg, 'draw_norm', False)
	xtick_rotation = get_param(cfg, 'xtick_rotation', 90)
	invert = get_param(cfg, 'invert', False)
	ncols = len(get_param(cfg, 'srcs')) if subplots else 1
	xlim = get_param(cfg, 'xlim')
	remaining_color = get_param(cfg, 'remaining_color', 'grey')
	remaining_label = get_param(cfg, 'remaining_label', 'Remaining')
	yticklabelfontsize = get_param(cfg, 'yticklabelfontsize', fontsize)
	annotate = get_param(cfg, 'annotate', False)

	if invert: invert = -1
	else: invert = 1

	fig, axes = plt.subplots(1, ncols, figsize=(width, height))
	axes = axes if subplots else [axes]
	dax = None

	labels = []
	minor_ticks = [0.]
	minor_labels = []
	major_ticks = [0.]
	major_labels = []
	supermajor_labels = []
	supermajor_ticks = [0.]
	subplots_xlims = []
	addx = []
	for group_idx, group in enumerate(get_param(cfg, 'srcs')):
		if type(group) is not list:
			group = [group]

		minor_ticks_len = len(minor_ticks)
		major_tick = 0
		subplots_xlims.append((minor_ticks[-1], 0))
		for bar_idx, bar in enumerate(group):
			ax = axes[group_idx] if subplots else axes[0]

			src = get_param(bar, 'src')
			scale = get_param(bar, 'scale', 1)
			minor_label = get_param(bar, 'label', '')
			stack = get_param(bar, 'stack')
			dual = get_param(bar, 'dual', False)
			showx = get_param(bar, 'x', False)

			if dual:
				dax = ax.twinx() if dax is None else dax
				ax = dax

			minor_labels.append(minor_label)
			minor_ticks.append(minor_ticks[-1] + minor_spacing)
			if bar_idx == 0: 
				minor_ticks[-1] += major_spacing
				if (group_idx % supermajor_index) == 0:
					minor_ticks[-1] += supermajor_spacing
			major_tick += minor_ticks[-1]

			running_height = 0
			stack = get_param(cfg, 'stacks.%s' % stack)

			if showx:
				addx.append((ax, minor_ticks[-1]))
				continue

			with open(src, 'r') as f:
				data = json.load(f)

			normalize = 1.
			if 'normalize' in bar:
				norm_bar = get_param(bar, 'normalize')
				norm_stack = get_param(cfg, 'stacks.%s' % \
					get_param(norm_bar, 'stack'))
				with open(get_param(norm_bar, 'src'), 'r') as f:
					ref_data = json.load(f)

				if 'total' in norm_stack:
					_, normalize = get(ref_data, get_param(norm_stack, 'total'))
				else:
					normalize = 0
					for key_idx, key in enumerate(get_param(norm_stack, 'keys')):
						if type(key) is list:
							for k in key:
								f, t = get(ref_data, k)
								if not f: break
								normalize += t

							if not f: continue
						else: 
							f, d = get(ref_data, key)
							if not f: continue
							normalize += d

				normalize *= scale

			for key_idx, key in enumerate(get_param(stack, 'keys')):
				label = get_param(stack, 'labels')[key_idx]

				d = 0
				if type(key) is list:
					for k in key:
						f, t = get(data, k)
						if not f: break
						d += t

					if not f: continue
				else: 
					f, d = get(data, key)
					if not f: continue

				d *= scale
				color = colors[key_idx] if key_idx < len(colors) else 'grey'
				if 'colors' in stack:
					color = get_param(stack, 'colors.[%d]' % key_idx)

				bar = ax.bar(minor_ticks[-1], (d / normalize) ** invert, 
					barwidth, running_height, color=color, 
						label=label if label not in labels else '_nolegend_')

				if not overlay: running_height += (d / normalize) ** invert
				if label not in labels: 
					labels.append(label)

			if 'total' in stack:
				_, total = get(data, get_param(stack, 'total'))
				d = total * (scale / normalize) ** invert
				d -= running_height
				if d < 0: d = 0
				print('%s => total: %s remaining: %s' % (src, total, d))
				# if d < 0.1: continue 

				bar = ax.bar(minor_ticks[-1], d, 
					barwidth, running_height, color=remaining_color, 
					label=remaining_label if remaining_label not in labels else '_nolegend_')

				if remaining_label not in labels: 
					labels.append(remaining_label)

			if annotate:
				for p in bar:
					height = p.get_height()
					s = f'{height:.1f}'
					if height < 1:
						s = f'{height:.2f}'
					ax.annotate(s,
						xy=(p.get_x() + p.get_width() / 2, height),
						xytext=(0, 4), # 3 points vertical offset
						textcoords="offset points",
						ha='center', va='bottom')

		subplots_xlims[-1] = (subplots_xlims[-1][0], minor_ticks[-1])
		major_labels.append(get_param(cfg, 'major.[%d]' % group_idx, ''))
		major_ticks.append(major_tick / (len(minor_ticks) - minor_ticks_len))

	for ax, pos in addx:
		ax.text(pos, 0, 'x', 
			ha='center', fontsize=(2 * fontsize), color='red')

	for i, ax in enumerate(axes):
		ax.tick_params(axis='x', which='minor', labelsize=fontsize, 
			pad=minor_padding, rotation=minor_rotation)
		ax.set_xticks([tick + 0.02 for tick in minor_ticks[1:]], minor=True)
		ax.set_xticklabels(minor_labels, minor=True, rotation=xtick_rotation)

		ax.tick_params(axis='x', which='major', labelsize=fontsize, 
			pad=major_padding, rotation=major_rotation, bottom=False)
		ax.set_xticks(major_ticks[1:])
		ax.set_xticklabels(major_labels)
		ax.grid(False, axis='x', which='major')
		minx, maxx = subplots_xlims[i]
		minx += minor_spacing + major_spacing - barwidth # - barwidth / 2
		maxx += major_spacing # - barwidth/2
		if subplots: ax.set_xlim(minx, maxx)
		elif xlim: ax.set_xlim(*xlim)

		ax.tick_params(axis='y', which='major', labelsize=yticklabelfontsize)
		ylim = get_param(cfg, 'ylim', max(ax.get_ylim()) * 1.025)
		if log: 
			ax.set_yscale('log')
		else:
			if type(ylim) is list:
				ax.set_ylim((0, ylim[i]))
			else:
				ax.set_ylim((0, ylim))
		if sci_not: 
			ax.yaxis.set_major_formatter(ScalarFormatterForceFormat())
			ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
			ax.yaxis.get_offset_text().set_fontsize(fontsize)
		if draw_norm:
			ax.plot(ax.get_xlim(), 
				[1.0, 1.0], '--', color='grey', linewidth=1.5)
			ax.margins(x=0.0)
			if not log: ax.set_ylim((0, max(1.05, max(ax.get_ylim()))))

	ylabel = ylabel.replace('$mu$', r'$\mu$')
	axes[0].set_ylabel(ylabel, fontsize=fontsize)

	if dax is not None:
		dax.set_ylabel(dual_label, fontsize=fontsize)
		dax.tick_params(axis='y', which='major', labelsize=yticklabelfontsize)
		ylim = get_param(cfg, 'ylim', max(dax.get_ylim()) * 1.025)
		dax.set_ylim((0, ylim))
		dax.grid(False, axis='y', which='major')
		if sci_not: 
			dax.yaxis.set_major_formatter(ScalarFormatterForceFormat())
			dax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
			dax.yaxis.get_offset_text().set_fontsize(fontsize)

	fig.tight_layout(rect=rect, w_pad=0.05)

	if args.legend is not None:
		hdls, lbls = axes[0].get_legend_handles_labels()
		if dax is not None:
			dhdls, dlbls = dax.get_legend_handles_labels()
			hdls += dhdls
			lbls += dlbls

		if 'Remaining' in lbls and lbls.index('Remaining') != len(lbls) - 1:
			idx = lbls.index('Remaining')
			lbls[idx], lbls[-1] = lbls[-1], lbls[idx]
			hdls[idx], hdls[-1] = hdls[-1], hdls[idx]

		fig_legend = plt.figure(figsize=(len(lbls) * 2, 2))
		fig_legend.legend(hdls, lbls, loc='center', ncol=len(lbls))
				
	if args.legend is not None and not args.show:
		fig_legend.savefig(args.legend)	

	if args.dest is not None:
		fig.savefig(args.dest)
	elif args.show:
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
