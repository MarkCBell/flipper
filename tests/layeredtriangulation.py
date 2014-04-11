
from __future__ import print_function
try:
	import snappy
except ImportError:
	snappy = None

import flipper

RANDOM_WORD_LENGTH = 10

def main():
	if snappy is None:
		print('SnapPy required but unavailable, tests skipped.')
		return True
	
	tests = [
		('S_1_1', 'aB', 'm003'), ('S_1_1', 'aB', 'm004'),
		('S_1_1', 'Ba', 'm003'), ('S_1_1', 'Ba', 'm004'),
		('S_1_1', 'Ab', 'm003'), ('S_1_1', 'Ab', 'm004'),
		('S_1_1', 'bA', 'm003'), ('S_1_1', 'bA', 'm004'),
		('S_2_1', 'aaabcd', 'm036')
		]
	
	try:
		for surface, word, target_manifold in tests:
			S = flipper.examples.abstracttriangulation.SURFACES[surface]()
			N = snappy.Manifold(target_manifold)
			if surface == 'S_1_1' or surface == 'S_0_4':
				Ms = S.mapping_class(word).splitting_sequence().snappy_manifolds()
				assert(any(M.is_isometric_to(N) for M in Ms))
			else:
				M = S.mapping_class(word).splitting_sequence().snappy_manifold()
				assert(M.is_isometric_to(N))
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	except flipper.ComputationError:
		return False  # Mapping class is probably reducible.
	except AssertionError:
		return False
	
	try:
		for _ in range(50):
			try:
				S = flipper.examples.abstracttriangulation.Example_S_1_1()
				word = S.random_word(RANDOM_WORD_LENGTH)
				Ms = S.mapping_class(word).splitting_sequence().snappy_manifolds()
				N = snappy.twister.Surface('S_1_1').bundle(word)
				assert(any(M.is_isometric_to(N) for M in Ms))
			except flipper.AssumptionError:
				pass  # Word we chose was not pA.
			except flipper.ComputationError:
				pass  # Mapping class is probably reducible.
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())

