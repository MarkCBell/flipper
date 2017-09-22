
from __future__ import print_function

import flipper
try:
	import snappy
except ImportError:
	snappy = None

from time import time

def test(surface, word, target):
	M = snappy.Manifold(target)
	# M = snappy.twister.Surface(surface).bundle(word)  # These should be the same.
	N = snappy.Manifold(flipper.load(surface).mapping_class(word).bundle().snappy_string())
	for _ in range(100):
		try:
			if M.is_isometric_to(N):
				return True
		except RuntimeError:
			pass  # SnapPy couldn't decide if these are isometric or not.
		M.randomize()
		N.randomize()
	
	return False

def main():
	database = 'census_monodromies'  # We could also load('knot_monodromies').
	print('Building mapping tori for each monodromy in:')
	print('\t%s' % database)
	
	unmatched = []
	
	for surface, word, target in flipper.census(database):
		print('Buiding: %s over %s (target %s).' % (word, surface, target))
		start_time = time()
		if not test(surface, word, target):
			print('Could not match %s on %s' % (word, surface))
			unmatched.append((surface, word, target))
		print('\tComputed in %0.3fs' % (time() - start_time))
	
	if unmatched:
		print('Unable to match:')
		for unmatch in unmatched:
			print(unmatch)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Process each entry in a census')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		if snappy is None:
			print('This example requires SnapPy.')
			print('Please install it and try again.')
		else:
			main()

