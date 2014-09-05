
from __future__ import print_function
from time import time

import flipper
import snappy

def test(splittings, M):
	for splitting in splittings:
		N = splitting.snappy_manifold()
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
	unmatched = []
	for surface, word, target in flipper.censuses.load('census_monodromies'):
		#surface, word, target = 'S_3_1', 'Ghabacbdce', 's194'  # Slow ~50s.
		#surface, word, target = 'S_3_1', 'abcdeGh', 's451'  # Slow ~66s.
		#surface, word, target = 'S_2_1', 'abCDEf', 'm160'  # No closers??
		#surface, word, target = 'S_2_1', 'abCDE', 'v2099'  # No closers??
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		M = snappy.twister.Surface(surface).bundle(word)  # This should be the same as: M = snappy.Manifold(target)
		splittings = flipper.examples.template(surface).mapping_class(word).splitting_sequence()
		if not test(splittings, M):
			print('Could not match %s on %s' % (word, surface))
			unmatched.append((surface, word, target))
		if verbose: print('\tComputed in %f' % (time() - start_time))
	
	if unmatched:
		print('Unable to match:')
		for unmatch in unmatched:
			print(unmatch)

if __name__ == '__main__':
	main(verbose=True)

