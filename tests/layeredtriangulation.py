
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
		('aB', 'm003'), ('aB', 'm004'),
		('Ba', 'm003'), ('Ba', 'm004'),
		('Ab', 'm003'), ('Ab', 'm004'),
		('bA', 'm003'), ('bA', 'm004')
		]
	
	try:
		for word, target_manifold in tests:
			Ms = flipper.examples.abstracttriangulation.Example_S_1_1().mapping_class(word).splitting_sequence().snappy_manifolds()
			N = snappy.Manifold(target_manifold)
			assert(any(M.is_isometric_to(N) for M in Ms))
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

