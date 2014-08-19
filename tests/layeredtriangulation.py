
from __future__ import print_function
try:
	import snappy
except ImportError:
	snappy = None

import flipper

RANDOM_WORD_LENGTH = 10

def test(surface, word, target):
	S = flipper.examples.abstracttriangulation.SURFACES[surface]()
	splitting = S.mapping_class(word).splitting_sequence()
	# if splitting.closing_isometry is None or surface == 'S_1_1' or surface == 'S_0_4':
	if splitting.closing_isometry is None or surface == 'S_1_1' or surface == 'S_0_4':
		# we just have to try all of them.
		Ms = splitting.snappy_manifolds()
		assert(any(M.is_isometric_to(target) for M in Ms))
	else:
		M = splitting.snappy_manifold()
		assert(M.is_isometric_to(target))

def main(verbose=False):
	if snappy is None:  # !?! Should also check that the version is > 1.3.2 so that twister exists.
		print('SnapPy required but unavailable, tests skipped.')
		return True
	
	tests = [
		('S_1_1', 'aB', 'm003'), ('S_1_1', 'aB', 'm004'),
		('S_1_1', 'Ba', 'm003'), ('S_1_1', 'Ba', 'm004'),
		('S_1_1', 'Ab', 'm003'), ('S_1_1', 'Ab', 'm004'),
		('S_1_1', 'bA', 'm003'), ('S_1_1', 'bA', 'm004'),
		('S_2_1', 'aaabcd', 'm036'),
		('S_2_1', 'abcdeF', 'm038')
		]
	
	twister_tests = [
		('S_1_1', 'aB')
		]
	
	try:
		for surface, word, target_manifold in tests:
			if verbose: print(word)
			test(surface, word, snappy.Manifold(target_manifold))
		for surface, word in twister_tests:
			if verbose: print(word)
			test(surface, word, snappy.twister.Surface(surface).bundle(word))
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	except flipper.ComputationError:
		return False  # Mapping class is probably reducible.
	#except AssertionError:
	#	return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

