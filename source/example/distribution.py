
from __future__ import print_function

import flipper
import sys

def main(surface, length, sample=100):
	S = flipper.load(surface)
	count = 0
	for i in range(sample):
		mapping_class = S.mapping_class(length)
		if mapping_class.is_pseudo_anosov(): count += 1
		print('\rLength: %d, Computed %d/%d - %0.1f%% pA' % (length, (i+1), sample, float(count) * 100 / (i+1)), end='')
		sys.stdout.flush()

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Sample random words and compute the percentage that are pseudo-Anosov.')
	parser.add_argument('--surface', type=str, default='S_2_1', help='name of example surface to use')
	parser.add_argument('--length', type=int, default=10, help='length of words to generate')
	parser.add_argument('--sample', type=int, default=100, help='number of samples to take')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main(args.surface, args.length, args.sample)
