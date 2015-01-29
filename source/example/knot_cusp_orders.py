
from __future__ import print_function
from time import time

import flipper

def main(verbose=False):
	for surface, word, target in flipper.load.database('knot_monodromies'):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		stratum = flipper.load.equipped_triangulation(surface).mapping_class(word).stratum()
		vertex_orders = [stratum[singularity] for singularity in stratum]
		# A singularity is real if and only if its label is non-negative.
		real_vertex_orders = [stratum[singularity] for singularity in stratum if singularity.label >= 0]
		# This should be snappy.twister.Surface(surface).bundle(word) == snappy.Manifold(target)
		# But we wont bother to check this here.
		print('\tAll: %s, Real: %s' % (vertex_orders, real_vertex_orders))
		if verbose: print('\tComputed in %0.3fs' % (time() - start_time))

if __name__ == '__main__':
	main(verbose=True)

