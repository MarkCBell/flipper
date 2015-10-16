
from __future__ import print_function
from time import time

import flipper

def main():
	for surface, word, target in flipper.census('knot_monodromies'):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		stratum = flipper.load(surface).mapping_class(word).stratum()
		vertex_orders = [stratum[singularity] for singularity in stratum]
		# A singularity is real if and only if its label is non-negative.
		real_vertex_orders = [stratum[singularity] for singularity in stratum if not singularity.filled]
		# This should be snappy.twister.Surface(surface).bundle(word) == snappy.Manifold(target)
		# But we wont bother to check this here.
		print('\tAll: %s, Real: %s' % (vertex_orders, real_vertex_orders))

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Compute the singularity orders of knot complements.')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main()

