
from __future__ import print_function
from time import time

import flipper
import snappy

def stratum(splitting):
	lamination = splitting.initial_lamination
	stratum_orders = lamination.stratum_orders()
	vertex_orders = [stratum_orders[vertex] for vertex in lamination.triangulation.vertices]
	real_vertex_orders = [stratum_orders[vertex] for vertex in lamination.triangulation.vertices if vertex.label >= 0]
	return vertex_orders, real_vertex_orders

def test(splittings, M):
	for splitting in splittings:
		N = snappy.Manifold(splitting.bundle().snappy_string())
		for _ in range(300):
			M.randomize()
			N.randomize()
			try:
				if M.is_isometric_to(N):
					return True
			except RuntimeError:
				pass
	
	return False

def main(verbose=False):
	for surface, word, target in flipper.censuses.load('knot_monodromies'):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		splittings = flipper.examples.template(surface).mapping_class(word).splitting_sequence()
		print('\tAll: %s, Real: %s' % stratum(splittings[0]))
		M = snappy.twister.Surface(surface).bundle(word)  # This should be the same as: M = snappy.Manifold(target)
		if not test(splittings, M):
			print('Could not match %s on %s' % (word, surface))
		if verbose: print('\tComputed in %f' % (time() - start_time))

if __name__ == '__main__':
	main(verbose=True)

