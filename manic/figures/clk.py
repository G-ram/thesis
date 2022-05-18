import argparse

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
	return 1000000 / (delay_per_inv * invs)

def main(args):
	print('%f MHz' % get_freq((args.clk[0], args.clk[1])))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('clk', type=int, nargs=2, help='Clock tuple')
	args = parser.parse_args()		
	main(args)