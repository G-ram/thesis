import os
import argparse
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
mpl.rcParams['hatch.color'] = 'gray'
mpl.rcParams['hatch.linewidth'] = 0.6
style.use('bmh')

data = {
        'noc' : 138423.98,
        'fu' : 24647.788,
        'ucore' : 34989.70 + 45831.367, 
        'scalar' : 12666.903,
        'mem' : 245196.63,
        'cgra' : 253846.84,
        'total' : 512865.41,
        'cgra_remaining': None,
        'remaining': None
}

labels = {
        'fu' : 'FU',
        'ucore' : '$\mu$Core', 
        'noc' : 'NoC',
        'cgra_remaining': 'Other',
        'scalar' : 'Scalar',
        'mem' : 'Memory',
        # 'remaining' : 'Remaining'
}

groups = [['fu', 'ucore', 'noc', 'cgra_remaining'], ['scalar'], ['mem']]

colors = {
        'fu' : '#017528',
        'ucore' : '#258545', 
        'noc' : '#5a9c70',
        'cgra_remaining': '#a1dab4',
        'scalar' : '#41b6c4',
        'mem' : '#9f7ccf',
        'remaining': 'grey'
}

def pie(data, groups, labels, colors, radfraction=0.1, **kwargs):
        indices = [ (i,j) for i in range(len(groups))
                          for j in range(len(groups[i]))]
        # inverse_indices[i][j] = [ i where indices[i] == (i,j) ]
        inverse_indices = []
        for x in range(len(indices)):
                i, j = indices[x]
                if len(inverse_indices) < i + 1:
                        inverse_indices.append([])
                        assert len(inverse_indices) == i + 1
                if len(inverse_indices[i]) < j + 1:
                        inverse_indices[i].append(x)
                        assert len(inverse_indices[i]) == j + 1

        flatten = lambda arr: [arr[groups[i][j]] for i, j in indices]
        
        data = flatten(data)
        labels = flatten(labels)
        colors = flatten(colors)
        
        # print (groups)
        # print (indices)
        # print (inverse_indices)
        # print (data)
        # print (labels)
        # print (colors)
        # exit(0)

        ax = plt.gca()
        ax.set_aspect('equal')
        wedges, texts, percs = ax.pie(data, labels=labels, colors=colors, **kwargs)

        for group in inverse_indices:
            ang = np.deg2rad((wedges[group[-1]].theta2 + wedges[group[0]].theta1) / 2)
            for j in group:
                center = radfraction * wedges[j].r * np.array([np.cos(ang), np.sin(ang)])
                wedges[j].set_center(center)
                texts[j].set_position(np.array(texts[j].get_position()) + center)
                percs[j].set_position(np.array(percs[j].get_position()) + center)
        ax.autoscale(True)

def main(args):
        cgra_remaining = data['cgra'] - data['noc'] - data['fu'] - data['ucore']
        remaining = data['total'] - data['cgra'] - data['mem'] - data['scalar']
        data['cgra_remaining'] = cgra_remaining
        data['remaining'] = remaining

        for x in ['noc', 'fu', 'ucore']:
                print (x, data[x] / data['cgra'])

        def format(pct):
                if pct < 2: return ''
                return f'{pct:.1f}\%'

        fig, ax = plt.subplots(figsize=(3,3))
        
        pie(data=data,
            groups=groups,
            labels=labels,
            colors=colors,
            autopct=lambda pct: format(pct),
            radfraction = 0.05,
            startangle=90)

        fig.tight_layout(rect=[0, 0, 1, 0.9], w_pad=0.05)

        if args.dest:
                fig.savefig(args.dest)

        if args.show:
                plt.show()

if __name__ == '__main__':
        parser = argparse.ArgumentParser()
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
