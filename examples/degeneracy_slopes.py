
from __future__ import print_function

import flipper
import snappy

from time import time

def test(surface, word, target):
	splittings = flipper.load.equipped_triangulation(surface).mapping_class(word).splitting_sequences()
	# M = snappy.twister.Surface(surface).bundle(word)  # These should be the same.
	M = snappy.Manifold(target)
	for splitting in splittings:
		N = snappy.Manifold(splitting.bundle().snappy_string())
		for _ in range(100):
			M.randomize()
			N.randomize()
			try:
				if M.is_isometric_to(N):
					return True
			except RuntimeError:
				pass  # SnapPy couldn't decide if these are isometric or not.
	
	return False

def main(verbose=False):
	unmatched = []
	
	# We could also load('knot_monodromies').
	for surface, word, target in flipper.load.database('census_monodromies'):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		if not test(surface, word, target):
			print('Could not match %s on %s' % (word, surface))
			unmatched.append((surface, word, target))
		if verbose: print('\tComputed in %0.3fs' % (time() - start_time))
	
	if unmatched:
		print('Unable to match:')
		for unmatch in unmatched:
			print(unmatch)

if __name__ == '__main__':
	main(verbose=True)

