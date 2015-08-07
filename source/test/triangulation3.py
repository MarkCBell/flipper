
from __future__ import print_function
try:
	import snappy
except ImportError:
	snappy = None

import flipper

def test(surface, word, target):
	snappy_string = flipper.load(surface).mapping_class(word).bundle(canonical=False).snappy_string()
	# Snappy can fail with a RuntimeError, particularly when canonical=False.
	M = snappy.Manifold(snappy_string)
	for _ in range(100):
		try:
			if M.is_isometric_to(target):
				return True
		except RuntimeError:
			pass  # SnapPy couldn't decide if these are isometric or not.
		M.randomize()
	
	return False

def main(verbose=False):
	if verbose: print('Running layered triangulation tests.')
	
	if snappy is None:  # We really should check that the version is > 2.0.4 so that twister exists.
		print('SnapPy required but unavailable, tests skipped.')
		return True
	
	tests = [
		('S_1_1', 'aB', 'm004'),
		('S_1_1', 'Ba', 'm004'),
		('S_1_1', 'Ab', 'm004'),
		('S_1_1', 'bA', 'm004'),
		('S_1_1', 'aBababab', 'm003'),
		('S_1_1', 'Baababab', 'm003'),
		('S_1_1', 'Abababab', 'm003'),
		('S_1_1', 'bAababab', 'm003'),
		('S_1_1', 'aBaB', 'm206'), ('S_1_1', 'aBaBababab', 'm207'),  # Double covers.
		('S_1_2', 'abC', 'm129'),
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

