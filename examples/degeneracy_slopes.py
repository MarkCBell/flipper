
from __future__ import print_function
from time import time

import flipper
import snappy

def main(verbose=False):
	unmatched = []
	for surface, word, target in flipper.censuses.load('census_monodromies'):
		#surface, word, target = 'S_3_1', 'aaabacbdef', 's148'  # ERROR.
		#surface, word, target = 'S_3_1', 'abacbdceGh', 's194'  # Slow ~50s.
		#surface, word, target = 'S_3_1', 'abcdeGh', 's451'  # Slow ~66s.
		if verbose: print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		M = snappy.twister.Surface(surface).bundle(word)  # This should be the same as: M = snappy.Manifold(target)
		S = flipper.examples.template(surface)
		Bs = S.mapping_class(word).splitting_sequence().snappy_manifolds(name=word)
		try:
			if not any(B.is_isometric_to(M) for B in Bs):
				print('Could not match %s on %s' % (word, surface))
				print(M.volume(), M.homology(), M.chern_simons())
				print('with any of:')
				for B in Bs:
					print(B.volume(), B.homology(), B.chern_simons())
					print(B.identify())
				unmatched.append((surface, word, target))
		except RuntimeError:
			print('problems')
		if verbose: print('\tComputed in %f' % (time() - start_time))
	
	if unmatched:
		print('Unable to match:')
		for unmatch in unmatched:
			print(unmatch)

if __name__ == '__main__':
	main(verbose=True)

