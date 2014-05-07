
from __future__ import print_function

from time import time

import flipper
import snappy
from database import from_database

def main():
	for surface, word, target in from_database('census_monodromies'):
		print(target, word)
		start_time = time()
		M = snappy.twister.Surface(surface).bundle(word)  # This should be the same as: M = snappy.Manifold(target)
		S = flipper.examples.abstracttriangulation.SURFACES[surface]()
		Bs = S.mapping_class(word).splitting_sequence().snappy_manifolds(name=word)
		if not any(B.is_isometric_to(M) for B in Bs):
			print('Could not match %s on %s' % (word, surface))
			print(M.volume(), M.homology(), M.chern_simons())
			print('with any of:')
			for B in Bs:
				print(B.volume(), B.homology(), B.chern_simons())
				print(B.identify())
		print('Computed in %f' % (time() - start_time))

if __name__ == '__main__':
	main()

