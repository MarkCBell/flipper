import multiprocessing
from time import time
import flipper

length = 7
S = flipper.load('S_1_2')  # Get an EquippedTriangulation.

print('Building words of length at most %d.' % length)
start_time = time()
all_words = list(S.all_words(length))
print('Built %d words.' % len(all_words))
print('Completed in %0.3fs' % (time() - start_time))

print('Starting again in parallel.')
cores = 2
start_time = time()
all_words2 = list(S.all_words(length, cores=cores))
print('Built %d words.' % len(all_words2))
print('Completed in %0.3fs' % (time() - start_time))

print('Lists match: %s' % len(all_words) == len(set(all_words)) and set(all_words) == set(all_words2))

