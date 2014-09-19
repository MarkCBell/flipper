
from __future__ import print_function
from time import time

import flipper
import snappy

def stratum(splitting):
	lamination = splitting.initial_lamination
	stratum_orders = lamination.stratum_orders()
	vertex_orders = [stratum_orders[vertex] for vertex in lamination.triangulation.vertices]
	# A vertex is real if and only if its label is non-negative.
	real_vertex_orders = [stratum_orders[vertex] for vertex in lamination.triangulation.vertices if vertex.label >= 0]
	return vertex_orders, real_vertex_orders

def main(verbose=False):
	for surface, word, target in flipper.censuses.load('knot_monodromies'):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		splittings = flipper.examples.template(surface).mapping_class(word).splitting_sequences()
		print('\tAll: %s, Real: %s' % stratum(splittings[0]))
		if verbose: print('\tComputed in %f' % (time() - start_time))

if __name__ == '__main__':
	main(verbose=True)

