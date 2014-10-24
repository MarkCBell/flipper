
from __future__ import print_function
try:
	import snappy
except ImportError:
	snappy = None

import flipper

def test(surface, word, target):
	splittings = flipper.load.equipped_triangulation(surface).mapping_class(word).splitting_sequences()
	# Snappy can fail with a RuntimeError.
	return any(snappy.Manifold(splitting.bundle().snappy_string()).is_isometric_to(target) for splitting in splittings)

def main(verbose=False):
	if verbose: print('Running layered triangulation tests.')
	
	if snappy is None:  # We really should check that the version is > 2.0.4 so that twister exists.
		print('SnapPy required but unavailable, tests skipped.')
		return True
	
	tests = [
		('S_1_1', 'aB', 'm003'), ('S_1_1', 'aB', 'm004'),
		('S_1_1', 'Ba', 'm003'), ('S_1_1', 'Ba', 'm004'),
		('S_1_1', 'Ab', 'm003'), ('S_1_1', 'Ab', 'm004'),
		('S_1_1', 'bA', 'm003'), ('S_1_1', 'bA', 'm004'),
		('S_1_1', 'aBaB', 'm206'), ('S_1_1', 'aBaB', 'm207'),  # Double covers.
		('S_2_1', 'aaabcd', 'm036'),
		('S_2_1', 'abcdeF', 'm038')
		]
	
	twister_tests = [
		('S_1_1', 'aB')
		]
	
	try:
		for surface, word, target_manifold in tests:
			if verbose: print(word)
			if not test(surface, word, snappy.Manifold(target_manifold)):
				return False
		for surface, word in twister_tests:
			if verbose: print(word)
			if not test(surface, word, snappy.twister.Surface(surface).bundle(word)):
				return False
	except flipper.ComputationError:
		return False  # Mapping class is probably reducible.
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

