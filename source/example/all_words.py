
from __future__ import print_function

import flipper
import multiprocessing
from time import time

# We need a helper function that can be pickled for multiprocessing.
def helper(data):
	S, length, prefix, skip, filt = data
	return list(S.all_words(length, prefix=prefix, skip=skip, filter=filt))

# We'll add a filter. Words missing b, c, or a and x are definitely not pseudo-Anosov.
# So lets filter those out as they are boring.
def filt(word):
	return \
		('a' in word or 'A' in word or 'x' in word or 'X' in word) and \
		('b' in word or 'B' in word) and \
		('c' in word or 'C' in word)

def main(length, prefix_length, cores):
	# Get an EquippedTriangulation.
	S = flipper.load('S_1_2')
	
	# Note this will work even if you want to set additional flags, such as conjugacy=False.
	
	print('Building words of length at most %d.' % length)
	# One can generate all words directly.
	start_time = time()
	all_words = list(S.all_words(length, filter=filt))
	print('Built %d words.' % len(all_words))
	print('Completed in %0.3fs' % (time() - start_time))
	
	print('Starting again in parallel.')
	# Or use do the calculations in parallel.
	start_time = time()
	print('Generating skip list.')
	skip = S.generate_skip(4)  # We don't need to do this but it is well worth it.
	print('Built %d skip words.' % len(skip))
	print('Building prefixes of length at most %d.' % prefix_length)
	prefixes = [(S, length, prefix, skip, filt) for prefix in S.all_words(prefix_length, conjugacy=False, exact=True, skip=skip)]
	print('Built %d prefixes.' % len(prefixes))
	
	print('Starting %d subprocesses.' % cores)
	P = multiprocessing.Pool(processes=cores)
	print('Building words of length at most %d.' % length)
	results = P.map(helper, prefixes)
	all_words2 = list(S.all_words(prefix_length-1, skip=skip, filter=filt)) + [word for x in results for word in x]
	# This next section is trivial to multiprocess. If doing so one should definitely pass in the skip list.
	print('Built %d words.' % len(all_words2))
	print('Completed in %0.3fs' % (time() - start_time))
	
	if len(all_words) == len(set(all_words)) and set(all_words) == set(all_words2):
		print('Lists match.')
	else:
		print('Lists DONT match.')

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Generate all mapping classes of a given length')
	parser.add_argument('--length', type=int, default=7, help='length of words to generate')
	parser.add_argument('--prefix', type=int, default=3, help='length of prefix to split by')
	parser.add_argument('--cores', type=int, default=1, help='number of cores to use')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main(args.length, args.prefix, args.cores)

