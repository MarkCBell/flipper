
from __future__ import print_function

import flipper
from time import time

def main():
	S = flipper.load.equipped_triangulation('S_1_2')
	
	length = 4
	# Note this will work even if you want to set additional flags, such as conjugacy=False.
	
	# We'll add a filter. Words missing b, c, or a and x are definitely not pseudo-Anosov.
	# So lets filter those out as they are boring.
	filt = lambda word: ('a' in word or 'A' in word or 'x' in word or 'X' in word) and \
		('b' in word or 'B' in word) and \
		('c' in word or 'C' in word)
	
	print('Building words of length at most %d.' % length)
	# One can generate all words directly.
	start_time = time()
	X = list(S.all_words(length, filter=filt))
	print('Built %d words.' % len(X))
	print('Completed in %0.3fs' % (time() - start_time))
	
	print('Starting again.')
	# Or use this workaround which can be parallelised.
	start_time = time()
	prefix_length = 3
	print('Generating skip list.')
	skip = S.generate_skip(4)  # We don't need to do this but it is well worth it.
	print('Built %d skip words.' % len(skip))
	print('Building prefixes of length at most %d.' % prefix_length)
	Y = list(S.all_words(prefix_length, conjugacy=False, exact=True, skip=skip))
	print('Built %d prefixes.' % len(Y))
	# This next section can be trivially multiprocessed. If doing so one should definitely pass in the skip list.
	print('Building words of length at most %d.' % length)
	Z = list(S.all_words(prefix_length-1, skip=skip, filter=filt)) + [word for y in Y for word in S.all_words(length, prefix=y, skip=skip, filter=filt)]
	print('Built %d words.' % len(Z))
	
	if len(Z) == len(set(Z)) and set(Z) == set(X):
		print('Lists match.')
	else:
		print('Lists DONT match.')
	print('Completed in %0.3fs' % (time() - start_time))

if __name__ == '__main__':
	main()

