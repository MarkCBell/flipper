
from __future__ import print_function
from time import time

import flipper

def main(verbose=False):
	for surface, word, target in flipper.load.database('knot_monodromies'):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		lamination = flipper.load.equipped_triangulation(surface).mapping_class(word).splitting_sequence().lamination
		stratum_orders = lamination.stratum_orders()
		vertex_orders = [stratum_orders[vertex] for vertex in lamination.triangulation.vertices]
		# A vertex is real if and only if its label is non-negative.
		real_vertex_orders = [stratum_orders[vertex] for vertex in lamination.triangulation.vertices if vertex.label >= 0]
		# This should be snappy.twister.Surface(surface).bundle(word) == snappy.Manifold(target)
		# But we wont bother to check this here.
		print('\tAll: %s, Real: %s' % (vertex_orders, real_vertex_orders))
		if verbose: print('\tComputed in %0.3fs' % (time() - start_time))

if __name__ == '__main__':
	main(verbose=True)

