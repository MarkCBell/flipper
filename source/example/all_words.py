
from __future__ import print_function

import flipper
import multiprocessing
from time import time

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

def main():
	S = flipper.load.equipped_triangulation('S_1_2')
	
	length = 7
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
	prefix_length = 3
	print('Generating skip list.')
	skip = S.generate_skip(4)  # We don't need to do this but it is well worth it.
	print('Built %d skip words.' % len(skip))
	print('Building prefixes of length at most %d.' % prefix_length)
	prefixes = [(S, length, prefix, skip, filt) for prefix in S.all_words(prefix_length, conjugacy=False, exact=True, skip=skip)]
	print('Built %d prefixes.' % len(prefixes))
	cores = multiprocessing.cpu_count()
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
	main()

